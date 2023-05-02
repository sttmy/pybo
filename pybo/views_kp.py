from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from.models import Question, Answer, Comment
from django.utils import timezone
from.forms import QuestionForm, AnswerForm, CommentForm
from django.core.paginator import Paginator
from django.contrib import messages
from django import forms
import pymysql
# Create your views here.
from django.contrib.auth.decorators import login_required
def index(request):
    # -create_date로 해야 먼저작성한 글이 밀려 내려가게됨
    page = request.GET.get('page', '1') # 페이지
    question_list = Question.objects.order_by('-create_date')
    paginator = Paginator(question_list, 10) # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)
    context = {'question_list': page_obj}  # question_list는 페이징 객체(page_obj)
    # context = {'question_list': question_list} # 위에 context 사용으로 전에 써둔거 off
    return render(request, 'pybo/question_list.html', context)
    
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # pk = primary key 에 해당하는 값
    context = {'question': question}
    return render(request, 'pybo/question_detail.html', context)

@login_required(login_url='common:login') # 이걸로 로그인 제한
def answer_create(request, question_id):
    """
    pybo 답변등록
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.method =="POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user  # author 속성에 로그인 계정 저장
            answer.create_date = timezone.now()
            answer.question = question
            answer.save()
            return redirect('pybo:detail', question_id=question_id)
    else:
        form = AnswerForm()
        # return HttpResponseNotAllowed('Only Post is possible.') 3-7번에서 변경 후 사용 x
    context = {'question': question, 'form': form}
    return render(request, 'pybo/question_detail.html', context)
    # question.answer_set.create(content=request.POST.get('content'), create_date=timezone.now())
    # return redirect('pybo:detail', question_id=question.id)

def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid(): # 폼이 유효하다면
            question = form.save(commit=False) # 임시 저장하여 question 객체를 리턴받는다.
            question.author = request.user
            question.create_date = timezone.now() # 실제 저장을 위해 작성일시를 설정한다.
            question.save()   # 데이터를 실제로 저장한다
            return redirect('pybo:index')
    else:
        form = QuestionForm()
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)

@login_required(login_url='common:login')
def question_modify(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('pybo:detail', question_id=question.id)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.modify_date = timezone.now()  # 수정일시 저장
            question.save()
            return redirect('pybo:detail', question_id=question.id)
    else:
        form = QuestionForm(instance=question)
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)

@login_required(login_url='common:login')
def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('pybo:detail', question_id=question_id)
    question.delete()
    return redirect('pybo:index')
    # 위에서 미리 썼던건데 위에 쓴것으로 수정되었음
    # form = QuestionForm()
    # return render(request, 'pybo/question_form.html',
    #               {'form': form})

@login_required(login_url='common:login')
def answer_modify(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('pybo:detail', question_id=answer.question.id)
    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.modify_date = timezone.now()
            answer.save()
            return redirect('pybo:detail', question_id=answer.question.id)
    else:
        form = AnswerForm(instance=answer)
    context = {'answer': answer, 'form': form}
    return render(request, 'pybo/answer_form.html', context)

@login_required(login_url='common:login')
def answer_delete(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        answer.delete()
    return redirect('pybo:detail', question_id=answer.question.id)

@login_required(login_url='common:login')
def comment_create_question(request, question_id):
    """
    pybo 질문댓글등록
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = timezone.now()
            comment.question = question
            comment.save()
            return redirect('pybo:detail', question_id=question.id)
    else:
        form = CommentForm()
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)
@login_required(login_url='common:login')
def comment_modify_question(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, ' 댓글 수정권한이 없습니다')
        return redirect('pybo:detail', question_id=comment.question.id)
        return redirect('pybo:detail', question_id=comment.question.id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.modify_date = timezone.now()  # 수정일시 저장
            comment.save()
            return redirect('pybo:detail', question_id=comment.question.id)
    else:
        form = CommentForm(instance=comment)
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)

@login_required(login_url='common:login')
def comment_delete_question(request, comment_id):
    """
    pybo 질문댓글삭제
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓슬삭제권한이 없습니다.')
        return redirect('pybo:detail', question_id=comment.question_id)
    else:
        comment.delete()
    return redirect('pybo:detail', question_id=comment.question_id)

@login_required(login_url='common:login')
def comment_create_answer(request, answer_id):
    """
    pybo 답글댓글등록
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = timezone.now()
            comment.answer = answer
            comment.save()
            return redirect('pybo:detail', question_id=comment.answer.question.id)
    else:
        form = CommentForm()
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)


@login_required(login_url='common:login')
def comment_modify_answer(request, comment_id):
    """
    pybo 답글댓글수정
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글수정권한이 없습니다')
        return redirect('pybo:detail', question_id=comment.answer.question.id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.modify_date = timezone.now()
            comment.save()
            return redirect('pybo:detail', question_id=comment.answer.question.id)
    else:
        form = CommentForm(instance=comment)
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)


@login_required(login_url='common:login')
def comment_delete_answer(request, comment_id):
    """
    pybo 답글댓글삭제
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글삭제권한이 없습니다')
        return redirect('pybo:detail', question_id=comment.answer.question.id)
    else:
        comment.delete()
    return redirect('pybo:detail', question_id=comment.answer.question.id)




 ###########################################################################
# def tbl(request):
#     filename = "C:/tilburg_club/tilburg.txt"
#     with open(filename) as f:
#         root_ps = f.read().strip()
#     dev_ps = root_ps + 'dev'
#
#     conn = pymysql.connect(host='130.162.154.239', user='dev', password=dev_ps, db='For_Study_DB', charset='utf8')
#     cur = conn.cursor()
#     sql = "select * from For_Study_DB  where TBL_Question and TBL_Answer"
#     rows = cur.fetchall()
#     list1 = []
#     for row in rows:
#         boardClass = BoardClass(row[0],row[1],row[2])
#         list1.append(boardClass)
#     # request.session['list'] = list1
#     # print(rows)
#     context = {'board_list': list1}
#     return render(request, 'board/h_list.html', context)
#     # return render(request, "pybo/question_list", context )

# def question_list(request):
#      filename = "C:/tilburg_club/tilburg.txt"
#      with open(filename) as f:
#          root_ps = f.read().strip()
#      dev_ps = root_ps + 'dev'
#
#     # DB 연결
#     conn = pymysql.connect(host="130.162.154.239", user='dev', password='dev_ps', db='For_Study_DB', charset='utf8')
#     cur = conn.cursor()
#
#     # SQL 쿼리 실행
#     sql = """
#         SELECT Q.subject, Q.content, A.content
#         FROM TBL_Question Q
#         JOIN TBL_Answer A ON Q.subject = A.question;
#     """
#     cur.execute(sql)
#     rows = cur.fetchall()
#
#     # DB 연결 종료
#     cur.close()
#     conn.close()
#
#     # 데이터를 question_list2.html에 전달
#     context = {'question_list': rows}
#     return render(request, 'question_list2.html', context)



