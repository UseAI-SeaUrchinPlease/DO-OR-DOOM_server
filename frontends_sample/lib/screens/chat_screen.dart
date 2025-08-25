import 'package:flutter/material.dart';
import '../services/chat_api.dart';

class ChatScreen extends StatefulWidget {
  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ChatApi api = ChatApi();
  final TextEditingController _controller = TextEditingController();
  String _response = "";

  void _sendMessage() async {
    final reply = await api.sendMessage(_controller.text);
    setState(() {
      _response = reply;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Chat App")),
      body: Column(
        children: [
          Expanded(child: Center(child: Text(_response))),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(child: TextField(controller: _controller)),
                IconButton(icon: Icon(Icons.send), onPressed: _sendMessage),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
