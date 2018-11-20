#!/usr/bin/python3

import sys, os, argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import barbot.config

config = barbot.config.load()

from barbot.db import db, initializeDB, ModelError
from barbot.models.User import User


def addUser(args):
    try:
        user = User.addUser(args.username, args.fullname, args.password, args.admin)
        print('User {} added.'.format(user.name))
    except ModelError as e:
        print(str(e))
        sys.exit(1)

def deleteUser(args):
    try:
        User.deleteUser(args.username)
        print('User deleted.')
    except ModelError as e:
        print(str(e))
        sys.exit(1)
        
def userPassword(args):
    try:
        User.setUserPassword(args.username, args.password)
        print('Password set.')
    except ModelError as e:
        print(str(e))
        sys.exit(1)
        
def listUsers(args):
    for user in User.select():
        print('{}{} {}'.format('*' if user.isAdmin else '', user.name, user.fullName))
        
if __name__ == '__main__':
    initializeDB()
    
    parser = argparse.ArgumentParser(description = 'Barbot user administration tools')
    subparsers = parser.add_subparsers(dest = 'subparser', help = 'command help')
    
    subp = subparsers.add_parser('add', help = 'add help')
    subp.add_argument('username', help = 'the user\'s username')
    subp.add_argument('fullname', help = 'the user\'s full name')
    subp.add_argument('password', help = 'the user\'s password')
    subp.add_argument('--admin', action = 'store_true', help = 'is the user an administrator')
    subp.set_defaults(func = addUser)
    
    subp = subparsers.add_parser('delete', aliases = ['del'], help = 'delete help')
    subp.add_argument('username', help = 'the user\'s username')
    subp.set_defaults(func = deleteUser)
    
    subp = subparsers.add_parser('password', aliases = ['pw', 'passwd'], help = 'password help')
    subp.add_argument('username', help = 'the user\'s username')
    subp.add_argument('password', help = 'the user\'s password')
    subp.set_defaults(func = userPassword)
    
    subp = subparsers.add_parser('list', help = 'list help')
    subp.set_defaults(func = listUsers)
    
    args = parser.parse_args()
    args.func(args)
        
    

