# NintendoClients
Python package to communicate with Nintendo servers

To import this into your Python code, simply place the "nintendo" folder somewhere Python can find it.

Requirements:
* Python 3 (tested with 3.5.2)
* Python requests (http://docs.python-requets.org)
* BeautifulSoup4
* Nintendo SSL certificate (see below)

This code lacks documentation, but it does have a few example scripts:
* example_donkeykong.py downloads and prints DKC Tropical Freeze rankings, and downloads the replay file of the world record
* example_mariokart.py downloads and prints Mario Kart 8 rankings, and downloads a replay file
* example_miis.py requests and prints all kinds of information about the primary mii associated with a NNID
* example_friend_list.py requests and prints your friend list, incoming and outgoing friend requests, and blacklist
* example_friend_notifications.py listens for and prints friend notifications (when a friend starts a game for example)

Before you can access the account server, you have to place Nintendo's SSL client certificate in PEM format into the "files" folder named "wiiu_common_cert.pem" and "wiiu_commmon_key.pem". These can be downloaded from Nintendo's update server (title id 0005001B-10054000). Some functions of the account server are only available after authentication. Authentication requires your Nintendo Network ID and password and serial number, device id, system version, region and country of your Wii U. To access specific game servers, you also need the game server id and sandbox access key of the server.

Useful information:
* https://github.com/Kinnay/NintendoClients/wiki

The PRUDP connection is more reliable now.
