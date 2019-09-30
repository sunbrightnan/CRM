# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import crm.models
import multiselectfield.db.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.EmailField(max_length=255, unique=True)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_admin', models.BooleanField(default=False)),
                ('name', models.CharField(verbose_name='名字', max_length=32)),
                ('mobile', models.CharField(verbose_name='手机', max_length=32, blank=True, null=True, default=None)),
                ('memo', models.TextField(verbose_name='备注', blank=True, null=True, default=None)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '账户信息',
                'verbose_name_plural': '账户信息',
            },
            managers=[
                ('objects', crm.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Campuses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='校区', max_length=64)),
                ('address', models.CharField(verbose_name='详细地址', max_length=512, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClassList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('course', models.CharField(verbose_name='课程名称', max_length=64, choices=[('LinuxL', 'Linux中高级'), ('PythonFullStack', 'Python高级全栈开发')])),
                ('semester', models.IntegerField(verbose_name='学期')),
                ('price', models.IntegerField(verbose_name='学费', default=10000)),
                ('memo', models.CharField(verbose_name='说明', max_length=100, blank=True, null=True)),
                ('start_date', models.DateField(verbose_name='开班日期')),
                ('graduate_date', models.DateField(verbose_name='结业日期', blank=True, null=True)),
                ('class_type', models.CharField(verbose_name='班额及类型', max_length=64, blank=True, null=True, choices=[('fulltime', '脱产班'), ('online', '网络班'), ('weekend', '周末班')])),
                ('campuses', models.ForeignKey(verbose_name='校区', to='crm.Campuses')),
            ],
        ),
        migrations.CreateModel(
            name='ConsultRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('note', models.TextField(verbose_name='跟进内容...')),
                ('status', models.CharField(verbose_name='跟进状态', max_length=8, choices=[('A', '近期无报名计划'), ('B', '1个月内报名'), ('C', '2周内报名'), ('D', '1周内报名'), ('E', '定金'), ('F', '到班'), ('G', '全款'), ('H', '无效')], help_text='选择客户此时的状态')),
                ('date', models.DateTimeField(verbose_name='跟进日期', auto_now_add=True)),
                ('delete_status', models.BooleanField(verbose_name='删除状态', default=False)),
                ('consultant', models.ForeignKey(verbose_name='跟进人', related_name='records', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ContractTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='合同名称', max_length=128, unique=True)),
                ('content', models.TextField(verbose_name='合同内容')),
                ('date', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CourseRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('day_num', models.IntegerField(verbose_name='节次', help_text='此处填写第几节课或第几天课程...,必须为数字')),
                ('date', models.DateField(verbose_name='上课日期', auto_now_add=True)),
                ('course_title', models.CharField(verbose_name='本节课程标题', max_length=64, blank=True, null=True)),
                ('course_memo', models.TextField(verbose_name='本节课程内容', max_length=300, blank=True, null=True)),
                ('has_homework', models.BooleanField(verbose_name='本节有作业', default=True)),
                ('homework_title', models.CharField(verbose_name='本节作业标题', max_length=64, blank=True, null=True)),
                ('homework_memo', models.TextField(verbose_name='作业描述', max_length=500, blank=True, null=True)),
                ('scoring_point', models.TextField(verbose_name='得分点', max_length=300, blank=True, null=True)),
                ('re_class', models.ForeignKey(verbose_name='班级', to='crm.ClassList')),
                ('teacher', models.ForeignKey(verbose_name='讲师', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('qq', models.CharField(verbose_name='QQ', max_length=64, unique=True, help_text='QQ号必须唯一')),
                ('qq_name', models.CharField(verbose_name='QQ昵称', max_length=64, blank=True, null=True)),
                ('name', models.CharField(verbose_name='姓名', max_length=32, blank=True, null=True, help_text='学员报名后，请改为真实姓名')),
                ('sex', models.CharField(verbose_name='性别', max_length=16, blank=True, null=True, default='male', choices=[('male', '男'), ('female', '女')])),
                ('birthday', models.DateField(verbose_name='出生日期', blank=True, null=True, default=None, help_text='格式yyyy-mm-dd')),
                ('phone', models.BigIntegerField(verbose_name='手机号', blank=True, null=True)),
                ('source', models.CharField(verbose_name='客户来源', max_length=64, default='qq', choices=[('qq', 'qq群'), ('referral', '内部转介绍'), ('website', '官方网站'), ('baidu_ads', '百度推广'), ('office_direct', '直接上门'), ('WoM', '口碑'), ('public_class', '公开课'), ('website_luffy', '路飞官网'), ('others', '其它')])),
                ('course', multiselectfield.db.fields.MultiSelectField(verbose_name='咨询课程', max_length=22, choices=[('LinuxL', 'Linux中高级'), ('PythonFullStack', 'Python高级全栈开发')])),
                ('class_type', models.CharField(verbose_name='班级类型', max_length=64, default='fulltime', choices=[('fulltime', '脱产班'), ('online', '网络班'), ('weekend', '周末班')])),
                ('customer_note', models.TextField(verbose_name='客户备注', blank=True, null=True)),
                ('status', models.CharField(verbose_name='状态', max_length=64, default='unregistered', choices=[('signed', '已报名'), ('unregistered', '未报名'), ('studying', '学习中'), ('paid_in_full', '学费已交齐')], help_text='选择客户此时的状态')),
                ('network_consult_note', models.TextField(verbose_name='网络咨询师咨询内容', blank=True, null=True)),
                ('date', models.DateTimeField(verbose_name='咨询日期', auto_now_add=True)),
                ('last_consult_date', models.DateField(verbose_name='最后跟进日期', auto_now_add=True)),
                ('next_date', models.DateField(verbose_name='预计再次跟进时间', blank=True, null=True)),
                ('class_list', models.ManyToManyField(verbose_name='已报班级', to='crm.ClassList')),
                ('consultant', models.ForeignKey(verbose_name='销售', blank=True, null=True, related_name='customers', to=settings.AUTH_USER_MODEL)),
                ('introduce_from', models.ForeignKey(verbose_name='转介绍自学员', blank=True, null=True, to='crm.Customer')),
                ('network_consultant', models.ForeignKey(verbose_name='咨询师', blank=True, null=True, related_name='network_consultant', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='部门名称', max_length=32)),
                ('count', models.IntegerField(verbose_name='人数', default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('why_us', models.TextField(verbose_name='为什么报名', max_length=1024, blank=True, null=True, default=None)),
                ('your_expectation', models.TextField(verbose_name='学完想达到的具体期望', max_length=1024, blank=True, null=True)),
                ('contract_agreed', models.BooleanField(verbose_name='我已认真阅读完培训协议并同意全部协议内容', default=False)),
                ('contract_approved', models.BooleanField(verbose_name='审批通过', default=False, help_text='在审阅完学员的资料无误后勾选此项,合同即生效')),
                ('enrolled_date', models.DateTimeField(verbose_name='报名日期', auto_now_add=True)),
                ('memo', models.TextField(verbose_name='备注', blank=True, null=True)),
                ('delete_status', models.BooleanField(verbose_name='删除状态', default=False)),
                ('customer', models.ForeignKey(verbose_name='客户名称', to='crm.Customer')),
                ('enrolment_class', models.ForeignKey(verbose_name='所报班级', to='crm.ClassList')),
                ('school', models.ForeignKey(to='crm.Campuses')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('pay_type', models.CharField(verbose_name='费用类型', max_length=64, default='deposit', choices=[('deposit', '订金/报名费'), ('tuition', '学费'), ('transfer', '转班'), ('dropout', '退学'), ('refund', '退款')])),
                ('paid_fee', models.IntegerField(verbose_name='费用数额', default=0)),
                ('note', models.TextField(verbose_name='备注', blank=True, null=True)),
                ('date', models.DateTimeField(verbose_name='交款日期', auto_now_add=True)),
                ('course', models.CharField(verbose_name='课程名', max_length=64, blank=True, null=True, default='N/A', choices=[('LinuxL', 'Linux中高级'), ('PythonFullStack', 'Python高级全栈开发')])),
                ('class_type', models.CharField(verbose_name='班级类型', max_length=64, blank=True, null=True, default='N/A', choices=[('fulltime', '脱产班'), ('online', '网络班'), ('weekend', '周末班')])),
                ('delete_status', models.BooleanField(verbose_name='删除状态', default=False)),
                ('status', models.IntegerField(verbose_name='审核', default=1, choices=[(1, '未审核'), (2, '已审核')])),
                ('confirm_date', models.DateTimeField(verbose_name='确认日期', blank=True, null=True)),
                ('confirm_user', models.ForeignKey(verbose_name='确认人', blank=True, null=True, related_name='confirms', to=settings.AUTH_USER_MODEL)),
                ('consultant', models.ForeignKey(verbose_name='销售', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(verbose_name='客户', to='crm.Customer')),
                ('enrolment_class', models.ForeignKey(verbose_name='所报班级', blank=True, null=True, to='crm.ClassList')),
            ],
        ),
        migrations.CreateModel(
            name='StudyRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('attendance', models.CharField(verbose_name='考勤', max_length=64, default='checked', choices=[('checked', '已签到'), ('vacate', '请假'), ('late', '迟到'), ('absence', '缺勤'), ('leave_early', '早退')])),
                ('score', models.IntegerField(verbose_name='本节成绩', default=-1, choices=[(100, 'A+'), (90, 'A'), (85, 'B+'), (80, 'B'), (70, 'B-'), (60, 'C+'), (50, 'C'), (40, 'C-'), (0, ' D'), (-1, 'N/A'), (-100, 'COPY'), (-1000, 'FAIL')])),
                ('homework_note', models.CharField(verbose_name='作业批语', max_length=255, blank=True, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('note', models.CharField(verbose_name='备注', max_length=255, blank=True, null=True)),
                ('homework', models.FileField(verbose_name='作业文件', blank=True, null=True, default=None, upload_to='')),
                ('course_record', models.ForeignKey(verbose_name='某节课程', to='crm.CourseRecord')),
                ('student', models.ForeignKey(verbose_name='学员', to='crm.Customer')),
            ],
        ),
        migrations.AddField(
            model_name='consultrecord',
            name='customer',
            field=models.ForeignKey(verbose_name='所咨询客户', to='crm.Customer'),
        ),
        migrations.AddField(
            model_name='classlist',
            name='contract',
            field=models.ForeignKey(verbose_name='选择合同模版', blank=True, null=True, to='crm.ContractTemplate'),
        ),
        migrations.AddField(
            model_name='classlist',
            name='teachers',
            field=models.ManyToManyField(verbose_name='老师', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='department',
            field=models.ForeignKey(blank=True, null=True, default=None, to='crm.Department'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='groups',
            field=models.ManyToManyField(verbose_name='groups', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_permissions',
            field=models.ManyToManyField(verbose_name='user permissions', blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission'),
        ),
        migrations.AlterUniqueTogether(
            name='studyrecord',
            unique_together=set([('course_record', 'student')]),
        ),
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together=set([('enrolment_class', 'customer')]),
        ),
        migrations.AlterUniqueTogether(
            name='courserecord',
            unique_together=set([('re_class', 'day_num')]),
        ),
        migrations.AlterUniqueTogether(
            name='classlist',
            unique_together=set([('course', 'semester', 'campuses')]),
        ),
    ]
