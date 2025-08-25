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

  // サーバーからのレスポンスを保存する変数
  Map<String, dynamic>? _positiveResponse;
  Map<String, dynamic>? _negativeResponse;

  void _addTask() {
    final String content = _textController.text;
    if (content.isNotEmpty) {
      setState(() {
        _tasks.add({"id": _tasks.length, "contents": content});
        // 新しいタスクを追加したら、前の応答はクリアする
        _positiveResponse = null;
        _negativeResponse = null;
      });
      _textController.clear();
    }
  }

  Future<void> _sendTasks() async {
    if (_tasks.isEmpty) {
      setState(() {
        _positiveResponse = {'text': '送信するタスクがありません。', 'image': null};
        _negativeResponse = null;
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
        final responseData = json.decode(utf8.decode(response.bodyBytes));
        setState(() {
          _positiveResponse = responseData['positive'];
          _negativeResponse = responseData['negative'];
          _tasks.clear(); // 送信成功後、リストをクリア
        });
      } else {
        setState(() {
          _positiveResponse = {
            'text': '送信失敗: ${response.statusCode}',
            'image': null,
          };
          _negativeResponse = {
            'text': 'エラー内容: ${response.body}',
            'image': null,
          };
        });
      }
    } catch (e) {
      setState(() {
        _positiveResponse = {'text': 'エラー: サーバーに接続できませんでした。', 'image': null};
        _negativeResponse = {'text': '$e', 'image': null};
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

              // タスク達成時の表示
              if (_positiveResponse != null)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12.0),
                  margin: const EdgeInsets.only(bottom: 20.0),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8.0),
                    border: Border.all(color: Colors.green.shade200),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'タスク達成時の様子:',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.green.shade700,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(_positiveResponse!['text']),
                      const SizedBox(height: 16),
                      if (_positiveResponse!['image'] != null)
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8.0),
                          child: Image.memory(
                            base64Decode(_positiveResponse!['image']),
                            fit: BoxFit.cover,
                          ),
                        ),
                    ],
                  ),
                ),

              // タスク未達成時の表示
              if (_negativeResponse != null)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12.0),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8.0),
                    border: Border.all(color: Colors.red.shade200),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'タスク未達成時の様子:',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.red.shade700,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(_negativeResponse!['text']),
                      const SizedBox(height: 16),
                      if (_negativeResponse!['image'] != null)
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8.0),
                          child: Image.memory(
                            base64Decode(_negativeResponse!['image']),
                            fit: BoxFit.cover,
                          ),
                        ),
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
