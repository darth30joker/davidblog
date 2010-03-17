#-*-coding:utf-8-*-

import MySQLdb
from MySQLdb.cursors import DictCursor

conn_david = MySQLdb.connect(host = 'localhost',
        user = 'root', passwd = 'root', db = 'davidblog',
        charset = 'utf8', cursorclass = DictCursor)

conn_wp = MySQLdb.connect(host = 'localhost',
        user = 'root', passwd = 'root', db = 'david_test',
        charset = 'utf8', cursorclass = DictCursor)

cursor_wp = conn_wp.cursor()
cursor_david = conn_david.cursor()
cursor_wp.execute(
        'SELECT ID, post_date, post_content, post_title '
        'FROM wp_posts WHERE post_status = "publish" '
        'AND post_type = "post" ORDER BY post_date ASC')
posts = cursor_wp.fetchall()

print 'Get %d posts' % len(posts)
for p in posts:
    cursor_david.execute(
            "INSERT INTO entries "
            "(`title`, `content`,  `createdTime`, `modifiedTime`, `slug`) "
            "VALUES ('%s', '%s', '%s', '%s', '%s')" % (p['post_title'].replace('"', '\\"').replace("'", "\\'"),
                p['post_content'].replace('"', '\\"').replace("'", "\\'"),
                p['post_date'], p['post_date'], 'test'))
    postId = conn_david.insert_id()
    conn_david.commit()
    print 'The insert id is %d' % postId
    cursor_wp.execute(
            'SELECT comment_author, comment_author_email, '
            'comment_author_url, comment_date, comment_content '
            'FROM wp_comments WHERE comment_post_ID = %s '
            'ORDER BY comment_date ASC' % p['ID'])
    comments = cursor_wp.fetchall()
    print 'Entry #%d has %d comments' % (postId, len(comments))
    if len(comments) > 0:
        for c in comments:
            cursor_david.execute(
                "INSERT INTO comments "
                "(entryId, username, email, url, comment, createdTime) "
                "VALUES (%s, '%s', '%s', '%s', '%s', '%s')" % (postId, c['comment_author'], c['comment_author_email'],
                    c['comment_author_url'],
                    c['comment_content'].replace('"', '\\"').replace("'", "\\'"), 
                    c['comment_date']))
            conn_david.commit()
        cursor_david.execute('UPDATE entries SET commentNum = %s WHERE id = %s' % (str(len(comments)), postId))
        conn_david.commit()
        print "Insert %d comments to entry #%d completed" % (len(comments), postId)
    print "Inserted %d posts" % len(posts)
