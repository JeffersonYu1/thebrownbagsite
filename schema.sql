DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    fname TEXT NOT NULL,
    lname TEXT NOT NULL,
    pref_f_name TEXT,
    pronouns TEXT,
    major TEXT,
    year TEXT,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    instagram TEXT,
    twitter TEXT,
    snapchat TEXT,
    SMS_check BIT, 
    iMessage_check BIT,
    Email_check BIT,
    GroupMe_check BIT,
    Messenger_check BIT,
    Instagram_check BIT,
    Snapchat_check BIT,
    Twitter_check BIT,
    interests TEXT NOT NULL
);