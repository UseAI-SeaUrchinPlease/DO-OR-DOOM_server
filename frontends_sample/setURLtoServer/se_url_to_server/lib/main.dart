import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

const server_url =
    'https://do-or-doom-server.onrender.com/set-sdserver'; // ここを適切なURLに変更

void main() {
  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(useMaterial3: true),
      home: const URLInputScreen(),
    );
  }
}

class URLInputScreen extends StatefulWidget {
  const URLInputScreen({super.key});

  @override
  State<URLInputScreen> createState() => _URLInputScreenState();
}

class _URLInputScreenState extends State<URLInputScreen> {
  final TextEditingController _urlController = TextEditingController();
  String _message = '';

  Future<void> _sendURL() async {
    try {
      final response = await http.post(
        Uri.parse(server_url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'url': _urlController.text}),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        setState(() {
          _message = responseData['message'];
        });
      } else {
        setState(() {
          _message = 'エラーが発生しました: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _message = 'エラーが発生しました: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Stable Diffusion Server URL設定')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                labelText: 'Stable Diffusion Server URL',
                hintText: 'https://example.com',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _sendURL, child: const Text('送信')),
            const SizedBox(height: 16),
            Text(
              _message,
              style: Theme.of(context).textTheme.bodyLarge,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }
}
