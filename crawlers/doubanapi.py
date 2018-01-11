#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: mcxiaoke
# @Date:   2015-08-26 12:35:52
from __future__ import print_function
import requests
import base64
import json
import sys

AUTH_TOKEN_URL = 'https://www.douban.com/service/auth2/token'
API_DOMAIN = 'https://api.douban.com/v2'

DFD_EDOMAIN = 'aHR0cHM6Ly9mcm9kby5kb3ViYW4uY29tL2FwaS92Mg=='
DFD_EKEY = 'MDdjNzg3ODJkYjAwYTEyMTE3NTY5Njg4OTEwMWUzNjM='
DFD_ESECRET = 'OTgxZGE5YjA5ODg3ZjEzZg=='
DFD_REDIRECT = 'aHR0cHM6Ly93d3cuZG91YmFuLmNvbS9hY2NvdW50cy9hdXRoMl9yZWRpcj91cmw9aHR0cDovL3NodW8uZG91YmFuLmNvbS8hc2VydmljZS9hbmRyb2lkJmFwaWtleT0gMDdjNzg3ODJkYjAwYTEyMTE3NTY5Njg4OTEwMWUzNjM='
DFD_EUA_FRODO = 'YXBpLWNsaWVudC8xIGNvbS5kb3ViYW4uZnJvZG8vNS4xOC4wLjAoOTgpIEFuZHJvaWQvMjEgY2FuY3JvX3djX2x0ZSBYaWFvbWkgTUkgNFcgIHJvbTptaXVpNg=='
DFD_EUA_SHUO = 'YXBpLWNsaWVudC8yLjMuMCBjb20uZG91YmFuLnNodW8vMi4yLjUoMTIxKSBBbmRyb2lkLzIxIGNhbmNyb193Y19sdGUgWGlhb21pIE1JIDRX'
UDID = '593d6cbdb087edc6ab268d38e96d1b94b44b8d72'


class ApiClient(object):

    def __init__(self, key=base64.b64decode(DFD_EKEY),
                 secret=base64.b64decode(DFD_ESECRET)):
        self.host = API_DOMAIN
        self.key = key
        self.secret = secret
        self.redirect_uri = base64.b64decode(DFD_REDIRECT)
        self.ua = base64.b64decode(DFD_EUA_SHUO)
        self.udid = UDID
        self.id = None
        self.tk = None
        print('host={}, apikey={}, udid={}, ua={}'
              .format(self.host, self.key, self.udid, self.ua))

    def log_request(self, r):
        #print('[HTTP] {} {} ({}:{})'.
        #      format(r.request.method, r.url, r.status_code, r.reason))
        pass

    def _get_url(self, url, params=None, **options):
        headers = {
            'User-Agent': self.ua
        }
        if self.id and self.tk:
            headers['Authorization'] = 'Bearer {0}'.format(self.tk)
        if not params:
            params = {}
        params['apikey'] = self.apikey
        params['udid'] = self.udid
        params['channel'] = 'Douban'
        r = requests.get(url, params=params, headers=headers, **options)
        log_request(r)
        if r.status_code >= 400:
            print(r.text)
        return r.json()

    def _post_url(self, url, payload=None, files=None, **options):
        headers = {
            'User-Agent': self.ua
        }
        if self.id and self.tk:
            headers['Authorization'] = 'Bearer {0}'.format(self.tk)
        if not payload:
            payload = {}
        params = {}
        params['apikey'] = self.key
        params['udid'] = self.udid
        params['channel'] = 'Douban'
        r = requests.post(url,
                          params=params, data=payload, files=files,
                          headers=headers, **options)
        self.log_request(r)
        if r.status_code >= 400:
            print(r.text)
        return r.json()

    def _get(self, path, params=None, **options):
        return _get_url(self.host + path, params, options)

    def _post(self, path, payload=None, **options):
        return _get_url(self.host + path, params, options)

    def login(self, username, password):
        headers = {
            'User-Agent': self.ua
        }
        payload = {
            'client_id': self.key,
            'client_secret': self.secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'password',
            'username': username,
            'password': password
        }
        r = requests.post(AUTH_TOKEN_URL, data=payload, headers=headers)
        self.log_request(r)
        res = r.json()
        self.id = res.get('douban_user_id')
        self.tk = res.get('access_token')
        if self.id:
            print('login successful! token=', self.tk)
        else:
            print('login failed!', res)
        return res

    def me(self):
        if self.id:
            return requests.get(API_DOMAIN + 'user/' + self.id).json()
        else:
            print('error: unable to get self info, not logined.')

    def album_info(self, id):
        # GET /photo_album/:id
        return self._get('/photo_album/%s' % id)

    def album_like(self, id):
        # POST/photo_album/:id/like
        return self._post('/photo_album/%s/like' % id)

    def album_unlike(self, id):
        # POST /photo_album/:id/unlike
        return self._post('/photo_album/%s/unlike' % id)

    def album_photos(self, id, start=0, count=20):
        # GET /photo_album/:id/photos?start=&count=
        params = {'start': start, 'count': count}
        return self._get('/photo_album/%s/photos' % id, params)

    def user_albums(self, id, start=0, count=20):
        # GET /user/:id/photo_albums?start=&count=
        params = {'start': start, 'count': count}
        return self._get('/user/%s/photo_albums' % id, params)

    def user_notes(self, id, start=0, count=20):
        # GET /user/:id/notes?start=&count=
        params = {'start': start, 'count': count}
        return self._get('/user/%s/notes' % id, params)

    def user_likes(self, id, cat, start=0, count=20):
        # GET /v2/user/:id/likes
        # cat ’all’, ‘note’, ‘photo_album’, ‘photo’, ‘online’, ‘topic’, ‘experience’, ‘dongxi’
        params = {'cat': cat, 'start': start, 'count': count}
        return self._get('/user/%s/likes' % id, params)

    def user_items(self, id):
        # GET /v2/user/:id/itemlist
        return self._get('/user/%s/itemlist' % id)

    def user_collect(self, id, type, start=0, count=20):
        # GET /v2/user/:id/collect_items
        # start,count,type  ‘movie’, ‘book’, ‘music’, ‘game’, ‘app’
        params = {'type': type, 'start': start, 'count': count}
        return self._get('/user/%s/collect_items' % id, params=params)

    def user_follow(self, id):
        # POST /v2/user/:id/follow
        return self._post('/user/%s/follow' % id)

    def user_unfollow(self, id):
        # POST /v2/user/:id/unfollow
        return self._post('/user/%s/unfollow' % id)

    def user_followings(self, id, start=0, count=20):
        # GET /v2/user/:id/following
        params = {'start': start, 'count': count}
        return self._get('/user/%s/following' % id, params=params)

    def user_followers(self, id, start=0, count=20):
        # GET /v2/user/:id/followers
        params = {'start': start, 'count': count}
        return self._get('/user/%s/followers' % id, params=params)

    def user_timeline(self, id, since_id=None, max_id=None):
        # GET /lifestream/user_timeline/
        params = {'since_id': since_id, 'max_id': max_id}
        r = requests.get(API_DOMAIN + '/lifestream/user_timeline/%s' % s, params=params)
        return r.json()

    def movie_info(self, id):
        # GET /v2/movie/:id
        return self._get('/movie/%s' % id)

    def tv_info(self, id):
        # GET /v2/tv/:id
        return self._get('/tv/%s' % id)

    def book_info(self, id):
        # GET /v2/book/:id
        return self._get('/book/%s' % id)

    def music_info(self, id):
        # GET /v2/music/:id
        return self._get('/music/%s' % id)

    def doulist_info(self, id):
        # GET /v2/doulist/:name
        return self._get('/doulist/%s' % id)

    def doulist_items(self, id):
        # GET /v2/doulist/:name/items start count
        return self._get('/doulist/%s/items' % id)

    def doulist_add(self, id, foreign_type, foreign_item_id, comment=None):
        # POST /v2/doulist/:id/add_item
        # foreign_type
        # foreign_item_id
        # comment
        payload = {'foreign_type': foreign_type,
                   'foreign_item_id': foreign_item_id,
                   'comment': comment}
        return self._post('/doulist/%s/add_item' % id, data=payload)

    def doulist_follow(self, id):
        # POST /v2/doulist/:name/follow
        return self._post('/doulist/%s/follow' % id)

    def doulist_unfollow(self, id):
        # POST /v2/doulist/:name/unfollow
        return self._post('/doulist/%s/unfollow' % id)

    def doulist_create(self, title, desc=None, tags=None):
        # POST /v2/doulist/create
        # title, desc, tags
        payload = {'title': title, 'desc': desc, 'tags': tags}
        return self._post('/doulist/create', data=payload)

    def group_info(self, id):
        # GET /v2/group/:id
        return self._get('/group/%s' % id)

    def group_topics(self, id):
        # GET /v2/group/:id/topics
        return self._get('/group/%s/topics' % id)

    def group_topic(self, id):
        # GET /v2/group/topic/:id
        return self._get('/group/topic/%s' % id)

    def group_topic_comments(self, id):
        # GET /v2/group/topic/:id/comments
        return self._get('/group/topic/%s/comments' % id)

    def photo_upload(self, id, image, desc=None):
        # http://api.douban.com/v2/album/:id
        # POST /v2/album/:id
        # image = photo
        url = "https://api.douban.com/v2/album/%s" % id
        files = {'image': open(image, 'rb')}
        payload = {'desc': desc or image}
        return self._post_url(url, payload=payload, files=files)


if __name__ == '__main__':
    api = ApiClient()
    print(api.login(sys.argv[1], sys.argv[2]))
    print(api.me())
