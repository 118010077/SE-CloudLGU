from django.core.serializers.json import DjangoJSONEncoder
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Forumpost, Forumcomment
from accounts.models import MyUser
import datetime
from django.db.models import F


@require_POST
def create_new_post(request):
    data = json.loads(request.body)
    postTitle = data['postTitle']
    postContent = data['postContent']
    postTag = data['postTag']
    userID = data['userID']

    new_post = Forumpost(Title=postTitle, Content=postContent, Tag=postTag)
    poster = MyUser.objects.get(id=userID)
    new_post.Poster = poster
    new_post.UpdateTime = datetime.datetime.now()
    new_post.Ctime = datetime.datetime.now()
    new_post.save()

    response = {'postID': new_post.id, 'success': True}
    return JsonResponse(response)

@require_POST
def delete_post(request):
    data = json.loads(request.body)
    postID = data['postID']
    Forumpost.objects.get(id=postID).delete()
    response = {'success': True}
    return JsonResponse(response)


@require_POST
def update_post(request):
    data = json.loads(request.body)
    postID = data['postID']
    postTitle = data['postTitle']
    postContent = data['postContent']
    postTag = data['postTag']
    my_post = Forumpost.objects.get(id=postID)
    my_post.Title = postTitle
    my_post.Content = postContent
    my_post.Tag = postTag
    my_post.UpdateTime = datetime.datetime.now()
    my_post.save()

    response = {'postID': my_post.id, 'success': True}
    return JsonResponse(response)


def show_post(request):
    data = json.loads(request.body)
    postID = data['postID']
    my_post = Forumpost.objects.get(id=postID)
    comment_list = my_post.comments.annotate(userID=F('Commenter__id'),
                                             commentContent=F('Content'),
                                             createTime=F('Ctime'), commenterName=F('Commenter__username'),
                                             commentID=F('id')).values('commenterName',
                                                                       'userID',
                                                                       'commentContent',
                                                                       'createTime',
                                                                       'commentID')
    json_list = json.dumps(list(comment_list), cls=DjangoJSONEncoder)

    response = {'success': True, 'postTitle': my_post.Title, 'postContent': my_post.Content, 'postTag': my_post.Tag,
                'posterName': my_post.Poster.username, 'createTime': my_post.Ctime, 'updateTime': my_post.UpdateTime,
                'commentList': json.loads(json_list)}
    return JsonResponse(response)


def show_all_post(request):
    post_list = Forumpost.objects.annotate(postID=F('id'), postTitle=F('Title'),
                                           postContent=F('Content'),
                                           postTag=F('Tag'), posterName=F('Poster__username'),
                                           updateTime=F('UpdateTime'), createTime=F('Ctime')).values('postID',
                                                                                                     'postTitle',
                                                                                                     'postContent',
                                                                                                     'postTag',
                                                                                                     'posterName',
                                                                                                     'updateTime',
                                                                                                     'createTime')
    json_list = json.dumps(list(post_list), cls=DjangoJSONEncoder)
    response = {'success': True, 'postList': json.loads(json_list)}
    return JsonResponse(response)


def create_new_comment(request):
    data = json.loads(request.body)
    postID = data['postID']
    userID = data['userID']
    commentContent = data['commentContent']
    commenter = MyUser.objects.get(id=userID)
    my_post = Forumpost.objects.get(id=postID)
    new_comment = Forumcomment(forumPost=my_post, Content=commentContent)
    new_comment.Commenter = commenter
    new_comment.Ctime = datetime.datetime.now()
    my_post.UpdateTime = datetime.datetime.now()
    my_post.save()
    new_comment.save()

    response = {'commentID': new_comment.id, 'success': True}
    return JsonResponse(response)


def delete_comment(request):
    data = json.loads(request.body)
    commentID = data['commentID']
    Forumcomment.objects.get(id=commentID).delete()
    response = {'success': True}
    return JsonResponse(response)


def update_comment(request):
    data = json.loads(request.body)
    commentID = data['commentID']
    postID = data['postID']
    commentContent = data['commentContent']
    my_post = Forumpost.objects.get(id=postID)
    my_comment = Forumcomment.objects.get(id=commentID)
    my_comment.Content = commentContent
    my_post.UpdateTime = datetime.datetime.now()
    my_post.save()
    my_comment.save()
    response = {'success': True}
    return JsonResponse(response)
