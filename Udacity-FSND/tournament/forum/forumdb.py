#
# Database access functions for the web forum.
#
import psycopg2
import time
import bleach
bleach.clean('<script>')
bleach.clean('</script>')
bleach.clean('<script></script>')


## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    #posts = [{'content': str(row[1]), 'time': str(row[0])} for row in DB]
    #posts.sort(key=lambda row: row['time'], reverse=True)
    DB = psycopg2.connect("dbname=forum")
    cursor = DB.cursor();
    cursor.execute('select time,content from posts order by time desc')
    #cursor.execute("delete content from posts")
    data = cursor.fetchall()

    bleach.clean(data)
    u'an &lt;script&gt;evil()&lt;/script&gt; example'
    bleach.clean(u'<script>')
    bleach.clean(u'</script>')
    bleach.clean(u'<script></script>')
    bleach.clean(data, '<script>')

    print('bl-1')
    posts = ({'content': str(row[1]), 'time': str(row[0])} for row in data)
    bleach.clean(posts)
    DB.close()
    bleach.clean(posts, '<script>')
    bleach.clean(u'</script>')
    bleach.clean(u'<script></script>')
    return posts

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
    bleach.clean(content)
    u'an &lt;script&gt;evil()&lt;/script&gt; example'
    bleach.clean(u'<script>')
    bleach.clean(u'</script>')
    bleach.clean(u'<script></script>')
    print('bl-2')
    #t = time.strftime('%c', time.localtime())
    #DB.append((t, content))

    DB = psycopg2.connect("dbname=forum")
    cursor = DB.cursor()
    cursor.execute('insert into posts (content) values (%s)', (content, ) )
    #cursor.execute("delete content from posts")
    DB.commit()
    DB.close()
