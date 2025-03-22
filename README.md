# About
Some telegram users may have encountered the problem of large amounts of spam if they had not previously set up privacy in their account 🥴

This project allows you to flexibly configure the process of cleaning unnecessary chats 🧹🧹

# How to start
0. Move to directory "clear_tg_from_spam" and create virtual environment
```bash
cd clear_tg_from_spam
python -m venv venv
source venv/bin/activate
```
1. Install the required libraries
```python
pip install -r requirements.txt
```
2. Copy .env file
```bash
cp .env_example .env
```
3. Fill `API_ID` and `API_HASH` in .env file
```bash
nano .env
```
Then change `API_ID` and `API_HASH` to yours (you can find it on the [website](https://my.telegram.org)). Also you can change other projects parameters

4. Run this command to start the Cleaner
```bash
python main.py
```
On first launch you will need to create a session and then re-run this command

# Functional
You can configure the cleaner on .env file
- NUMBER_OF_WORKERS. Workers perform parallel operations with different chats. By default there is ***20*** workers
- UNREAD_COUNT_TRIGGER. If unread count > trigger than the dialog will be delete. ***1000*** by default

 - COUNT_OF_MY_MESSAGE_TRIGGER_FOR_GROUP. If count of my message > trigger than the dialog will be safe. ***6*** by default 

- COUNT_OF_MY_MESSAGE_TRIGGER_FOR_PERSONAL_CHAT. Is similar to previous one. ***5*** by default
