# coding: utf8

from news_stats import get_milestones


class TestNewsStats(object):
    def test_milestone_detection(self):
        old = [
            ('mg', 'wiktionary',
             {'articles': 100, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('az', 'wiktionary',
             {'articles': 202, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('dv', 'wiktionary',
             {'articles': 100, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('kz', 'wiktionary',
             {'articles': 212, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('dj', 'wiktionary',
             {'articles': 122, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('pa', 'wiktionary',
             {'articles': 202, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('de', 'wiktionary',
             {'articles': 100, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('ke', 'wiktionary',
             {'articles': 202, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('es', 'wiktionary',
             {'articles': 1, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0, 'images': 0,
              'queued-massmessages': 0, 'pages': 67}),
            ('ml', 'wiktionary',
             {'articles': 100, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('kn', 'wiktionary',
             {'articles': 202, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('dk', 'wiktionary',
             {'articles': 100, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('kl', 'wiktionary',
             {'articles': 202, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('se', 'wiktionary',
             {'articles': 1, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0, 'images': 0,
              'queued-massmessages': 0, 'pages': 67}),
            ('sv', 'wiktionary',
             {'articles': 202, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('fi', 'wiktionary',
             {'articles': 100, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('uz', 'wiktionary',
             {'articles': 202, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('uk', 'wiktionary',
             {'articles': 1, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0, 'images': 0,
              'queued-massmessages': 0, 'pages': 67})
        ]

        new = [
            ('mg', 'wiktionary',
             {'articles': 100, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('az', 'wiktionary',
             {'articles': 202, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 30486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('dv', 'wiktionary',
             {'articles': 300, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('kz', 'wiktionary',
             {'articles': 412, 'jobs': 0, 'users': 10400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('dj', 'wiktionary',
             {'articles': 522, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 30486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('pa', 'wiktionary',
             {'articles': 602, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('de', 'wiktionary',
             {'articles': 10, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0, 'images': 0,
              'queued-massmessages': 0, 'pages': 67}),
            ('ke', 'wiktionary',
             {'articles': 702, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('es', 'wiktionary',
             {'articles': 820, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 30486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('ml', 'wiktionary',
             {'articles': 900, 'jobs': 0, 'users': 1431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('kn', 'wiktionary',
             {'articles': 1202, 'jobs': 0, 'users': 400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('dk', 'wiktionary',
             {'articles': 1200, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('kl', 'wiktionary',
             {'articles': 1502, 'jobs': 0, 'users': 2400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('se', 'wiktionary',
             {'articles': 2000, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('sv', 'wiktionary',
             {'articles': 3002, 'jobs': 0, 'users': 4400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('fi', 'wiktionary',
             {'articles': 4000, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('uz', 'wiktionary',
             {'articles': 5002, 'jobs': 0, 'users': 5400, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67}),
            ('uk', 'wiktionary',
             {'articles': 6000, 'jobs': 0, 'users': 431, 'admins': 0, 'edits': 3486, 'activeusers': 0,
              'images': 0, 'queued-massmessages': 0, 'pages': 67})
        ]

        expected = [
            ('az', 'wiktionary', 'over', 30000, 'edits'),
            ('kz', 'wiktionary', 'over', 10000, 'users'),
            ('dj', 'wiktionary', 'over', 30000, 'edits'),
            ('de', 'wiktionary', 'below', 10, 'articles'),
            ('es', 'wiktionary', 'over', 800, 'articles'),
            ('es', 'wiktionary', 'over', 30000, 'edits'),
            ('ml', 'wiktionary', 'over', 1000, 'users'),
            ('kn', 'wiktionary', 'over', 1000, 'articles'),
            ('dk', 'wiktionary', 'over', 1000, 'articles'),
            ('kl', 'wiktionary', 'over', 1000, 'articles'),
            ('kl', 'wiktionary', 'over', 2000, 'users'),
            ('se', 'wiktionary', 'over', 2000, 'articles'),
            ('sv', 'wiktionary', 'over', 3000, 'articles'),
            ('sv', 'wiktionary', 'over', 4000, 'users'),
            ('fi', 'wiktionary', 'over', 4000, 'articles'),
            ('uz', 'wiktionary', 'over', 5000, 'articles'),
            ('uz', 'wiktionary', 'over', 5000, 'users'),
            ('uk', 'wiktionary', 'over', 6000, 'articles')]

        got = [i for i in get_milestones(old, new)]
        got.sort()
        expected.sort()
        assert got == expected
