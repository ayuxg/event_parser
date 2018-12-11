#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
@version: ??
@author: li
@file: event_util.py
@time: 2018/11/29 8:39 PM
事件表示，事件的有效性判断
"""

import os
import time
import pickle
import datetime
import numpy as np
from src.cluster.singlePass import singlePassCluster
from src.cluster.singlePass.singlePassCluster import ClusterUnit
from src.utills import tfidf, data_process, dicts, keywords_extractor

corpus_train = "/Users/li/PycharmProjects/event_parser/src/text_full_full.txt"

data_process = data_process.DataPressing()


def events_list(news_title_list):
    for news in news_title_list:
        print news
    pass


def events_effectiveness(cluster_list, news_dict):
    """
    事件有效性判断
    :param cluster_list:
    :param news_dict:
    :return:
    """
    effectiveness_events = []
    non_effectiveness_events = []
    for cluster_index, cluster in enumerate(cluster_list):  # 遍历每一个事件类簇
        print "cluster: %s" % cluster_index  # 簇的序号
        print "node_list: %s" % cluster.node_list  # 该簇的节点列表
        centroid = cluster.centroid
        text_vectors_similarly = []
        for node in cluster.node_list:  # 提取每个事件类簇中的结点，并且计算每个节点的文本向量空间
            # 获取结点对应的新闻
            news = news_dict.get(str(node))
            # 将新闻转换成文本向量空间
            text_vector = tfidf.load_tfidf_vectorizer([news]).toarray().reshape(-1)
            # 计算每篇文章与类簇中心的相似度
            similarly = singlePassCluster.cosine_distance(text_vector, centroid)
            print "similarly %s " % similarly
            text_vectors_similarly.append(similarly)
        # 计算每个类簇中文章方差
        variance = np.var(text_vectors_similarly)
        print "variance: %s" % variance

        # 如果方差大于某个阈值，则为无效事件
        if variance >= 10000:
            non_effectiveness_events.append(cluster)
        else:
            effectiveness_events.append(cluster)

    print "length of effectiveness_events: %s" % len(effectiveness_events)
    print "length of non_effectiveness_events: %s" % len(effectiveness_events)
    return effectiveness_events, non_effectiveness_events


def event_expression(news_title_list, news_list):
    """
    事件表示，
    :return:
    """
    # 根据事件类簇中的新闻id，从原始
    stock_lists = []
    news_lists = []
    for news in news_list:
        # print news
        # 提取正文中提及到的股票代码
        content_list = news.split(" ")
        stock_list = data_process.find_stocks(content_list=content_list, stock_dicts=dicts.stock_dict)
        stock_lists.extend(stock_list)
        news_lists.extend(content_list)
    # 事件中涉及的股票
    stocks = ",".join(item for item in set(stock_lists))
    print "事件中包含的股票 %s" % stocks
    # 事件簇关健词提取
    new_string = ' '.join(item for item in news_lists)
    # print "事件类簇 %s" % new_string
    event_keywords = keywords_extractor.parallel_test(news_lists)
    event_keywords = ','.join(item for item in event_keywords)
    # print "事件关键词： %s" % event_keywords

    # for news_title in news_title_list:
    #     print news_title
    for news in news_list:
        print news
    return stock_lists, event_keywords


def load_history_event(event_unit_path=None):
    """
    导入历史事件单元库
    :param event_unit_path:
    :return:
    """
    if event_unit_path is None:
        path = "/Users/li/PycharmProjects/event_parser/src/"
        event_unit_path = path + 'model/event_units_new.pkl'
    print event_unit_path
    event_unit_lists = pickle.load(open(event_unit_path, 'rb'))

    print "事件库中事件的个数 %s" % len(event_unit_lists)
    # for index, event_unit in enumerate(event_unit_lists):
    #     print "cluster: %s" % index  # 簇的序号
    #     print event_unit.node_list  # 该簇的节点列表
    #     print event_unit.centroid

    return event_unit_lists


def event_save(event_units, save_name=None, save_path=None):
    if save_name is None:
        save_name = str(int(time.time()))
    if save_path is None:
        save_path = "../event_model/"
        print("[event_util Info]当前文件夹: %s" % save_path)
    clustering_path = save_path + '%s.pkl' % save_name
    with open(clustering_path, 'wb') as fw:
        pickle.dump(event_units, fw)


def event_load(save_path):
    """
    从文件夹中读取最新的事件单元保存文件。
    :param save_path: 目录地址
    :return:
    """
    lists = os.listdir(save_path)  # 列出目录的下所有文件和文件夹保存到lists
    lists.sort(key=lambda fn: os.path.getmtime(save_path + fn))  # 将文件按时间排序
    filetime = datetime.datetime.fromtimestamp(os.path.getmtime(save_path+lists[-1]))
    file_new = os.path.join(save_path, lists[-1])  # 获取最新的文件保存到file_new
    print("[event_util Info] 时间：" + filetime.strftime('%Y-%m-%d %H-%M-%S'))
    print("[event_util Info] 最新修改的文件(夹)：" + lists[-1])
    return file_new


# 重复性事件合并? 可以手动标记然后合并


class EventUnit(singlePassCluster.ClusterUnit):
    """
    定义一个事件单元
    """

    def __init__(self):
        ClusterUnit.__init__(self)
        self.event_id = ''
        self.title = " "
        self.keywords = []
        self.stocks = []

    def title_update(self):
        # 遍历节点列表
        pass

    def keywords_update(self):
        pass


class EventLib():
    def __init__(self):
        self.event_unit_list = []