import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatApi {
  final String baseUrl = "http://localhost:8000"; // Dockerで動いているAPI

  Future<String> sendMessage(String message) async {
    final response = await http.post(
      Uri.parse("$baseUrl/chat"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "messages": [
          {"role": "user", "content": message},
        ],
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final reply = data["reply"];
      if (reply is String) {
        return reply;
      } else {
        // dict が返ってきた場合は適当に文字列化する
        return jsonEncode(reply);
      }
    } else {
      throw Exception("Failed to send message: ${response.body}");
    }
  }
}
