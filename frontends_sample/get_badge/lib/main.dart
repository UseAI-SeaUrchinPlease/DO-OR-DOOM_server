import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

const server_url = 'https://do-or-doom-server.onrender.com/badge';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'バッジ生成アプリ',
      theme: ThemeData(primarySwatch: Colors.blue, useMaterial3: true),
      home: const BadgeScreen(),
    );
  }
}

class BadgeScreen extends StatefulWidget {
  const BadgeScreen({super.key});

  @override
  State<BadgeScreen> createState() => _BadgeScreenState();
}

class _BadgeScreenState extends State<BadgeScreen> {
  final List<Map<String, dynamic>> _tasks = [];
  final TextEditingController _textController = TextEditingController();
  Map<String, dynamic>? _response;
  bool _isLoading = false;

  void _addTask() {
    final String content = _textController.text;
    if (content.isNotEmpty) {
      setState(() {
        _tasks.add({"id": _tasks.length, "contents": content});
        _response = null;
      });
      _textController.clear();
    }
  }

  Future<void> _sendTasks() async {
    if (_tasks.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('タスクを追加してください')));
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final response = await http.post(
        Uri.parse(server_url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"mode": "today-tasks", "tasks": _tasks}),
      );

      if (response.statusCode == 200) {
        setState(() {
          _response = jsonDecode(utf8.decode(response.bodyBytes));
          _tasks.clear();
        });
      } else {
        throw Exception('サーバーエラー: ${response.statusCode}');
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('エラーが発生しました: $e')));
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('バッジ生成'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // タスク入力フィールド
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    decoration: const InputDecoration(
                      hintText: 'タスクを入力してください',
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: (_) => _addTask(),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(onPressed: _addTask, child: const Text('追加')),
              ],
            ),
            const SizedBox(height: 16),

            // タスクリスト
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _tasks.length,
              itemBuilder: (context, index) {
                return Card(
                  child: ListTile(
                    leading: CircleAvatar(child: Text('${index + 1}')),
                    title: Text(_tasks[index]['contents']),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete),
                      onPressed: () {
                        setState(() {
                          _tasks.removeAt(index);
                        });
                      },
                    ),
                  ),
                );
              },
            ),
            const SizedBox(height: 16),

            // 送信ボタン
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _sendTasks,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('バッジを生成'),
              ),
            ),
            const SizedBox(height: 24),

            // バッジ表示部分
            if (_response != null)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16.0),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(12.0),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // バッジ名
                    if (_response!['name'] != null) ...[
                      Text(
                        _response!['name'],
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],

                    // 説明文
                    if (_response!['text'] != null) ...[
                      Text(
                        _response!['text'],
                        style: const TextStyle(fontSize: 16),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // バッジ画像
                    if (_response!['image'] != null)
                      Center(
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(8.0),
                          child: Image.memory(
                            base64Decode(_response!['image']),
                            fit: BoxFit.cover,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
