 Online Interaction

## Important:
**Saving** and **Loading** for Online isn't needed! If you can make it work though, props to you.

Score: 3 points

![Alt Text](./Checkpoint3_gif/OnlineMovement.gif)

Example for rendering other players

- [x] (2 point) Currently Online can render other players' direction and moving state. (Implemented: direction + moving sync, online players use character animation)

(HINT 1: Try to figure out how to change animation direction first for your player. Then figure out how to render animation for online players; maybe you can check how online manager handles it?)

(HINT 2: We've added 'HINT:...' comments, check 'em out!)

![Alt Text](./Checkpoint3_gif/chat.gif)

- [ ] (1 point) Chat Mechanism. Implement a chat system for the online version.
(HINT: We've added a chat_overlay.py and some additional comments in game_scene.py)

**Guide to Run Online:**

Video guide: https://drive.google.com/file/d/1S3R6RD-XzZskEqNRjE9ytsM9qmjvTCth/view?usp=sharing

1. Open a terminal and run `python server.py`.
2. Open two other terminals and run `python main.py --online` on each (or set `ONLINE=1` env var). Optionally set server URL with `--server ws://host:port`.
3. Enjoy.