# groupChat-noGUI-sockets
integrantes do grupo:

Cauê Araújo Euzébio - 211028195
Levi de Sousa Silva - 200049356
Maria Tereza Oliveira da Luz Dantas - 211028210

This repository contains my project for the computer networks class.

It consists in two .py archives (client-noGUI.py and serverChat-noGUI.py).

This project was made using sockets and threads.

- implemanted functions:
  * /private <targetName> <message> : client can send message in a private chat;
  * /group <groupName> <message> : client can send a message in a groupchat;
  * /create <groupName> : client can create a group and add members;
  * /file <targetName> <fileName> : client can send media files in private or group chats;
  * /kick <targetName> <groupName> : client can remove any member from a group (if they're the group admin);
  * /quitGroup <groupName> : client can remove themselves of a groupchat;
  * /quit : client can quit and close the application;
  * /profile <targetName> : client can view profiles of other clients.
