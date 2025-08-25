import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Task App',
      theme: ThemeData(primarySwatch: Colors.blue, useMaterial3: true),
      home: const TaskScreen(),
    );
  }
}

class TaskScreen extends StatefulWidget {
  const TaskScreen({super.key});

  @override
  State<TaskScreen> createState() => _TaskScreenState();
}

class _TaskScreenState extends State<TaskScreen> {
  final List<Map<String, dynamic>> _tasks = [];
  final TextEditingController _textController = TextEditingController();

  // ▼▼▼ 変更点1：サーバーからの応答を保存する変数を追加 ▼▼▼
  String _serverResponse = '';

  void _addTask() {
    final String content = _textController.text;
    if (content.isNotEmpty) {
      setState(() {
        _tasks.add({"id": _tasks.length, "contents": content});
        // 新しいタスクを追加したら、前の応答はクリアする
        _serverResponse = '';
      });
      _textController.clear();
    }
  }

  Future<void> _sendTasks() async {
    if (_tasks.isEmpty) {
      setState(() {
        _serverResponse = "送信するタスクがありません。";
      });
      return;
    }

    final Map<String, dynamic> jsonData = {
      "mode": "today-tasks",
      "tasks": _tasks,
    };

    final url = Uri.parse('http://localhost:8000/dialy'); // Dockerで動いているAPIのURL

    // ▼▼▼ 変更点3：応答をsetStateで変数に保存する処理を追加 ▼▼▼
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode(jsonData),
      );

      if (response.statusCode == 200) {
        setState(() {
          // UTF-8でデコードして文字化けを防ぐ
          _serverResponse = utf8.decode(response.bodyBytes);
          _tasks.clear(); // 送信成功後、リストをクリア
        });
      } else {
        setState(() {
          _serverResponse =
              '送信失敗: ${response.statusCode}\nエラー内容: ${response.body}';
        });
      }
    } catch (e) {
      setState(() {
        _serverResponse = 'エラー: サーバーに接続できませんでした。\n$e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('今日のタスク'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      // SingleChildScrollViewを追加して、画面が溢れてもスクロールできるようにする
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              // (入力欄やタスクリストのUIは変更なし)
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
              const SizedBox(height: 20),
              // ListViewの高さを固定するか、ShrinkWrapを使う
              ListView.builder(
                shrinkWrap: true, // Columnの中でListViewを使うための設定
                physics: const NeverScrollableScrollPhysics(), // 親のスクロールを使う
                itemCount: _tasks.length,
                itemBuilder: (context, index) {
                  return Card(
                    child: ListTile(
                      leading: CircleAvatar(child: Text('${index + 1}')),
                      title: Text(_tasks[index]['contents']),
                    ),
                  );
                },
              ),
              const SizedBox(height: 20),

              // (送信ボタンのUIは変更なし)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _sendTasks,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('サーバーに送信'),
                ),
              ),
              const SizedBox(height: 20),

              // ▼▼▼ 変更点2：サーバーからの応答を表示するUIを追加 ▼▼▼
              if (_serverResponse.isNotEmpty)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12.0),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(8.0),
                    border: Border.all(color: Colors.grey.shade400),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'サーバーからの応答:',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.grey.shade700,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(_serverResponse),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
