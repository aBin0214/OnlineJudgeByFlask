#!/usr/bin/env python
# -*- coding:utf-8 -*-

class Problem():
    def __init__(self,id,title,create_by,time_limit,mem_limit):
        self.__id = id
        self.__title = title
        self.__create_by = create_by
        self.__time_limit = time_limit
        self.__time_limit = mem_limit

    def __str__(self):
        fmt = "problem id: {id},title: {title},create_by: {create_by},time_limit: {time_limit},mem_limit: {mem_limit}"
        return fmt.format(id=id,title=title,create_by=create_by,time_limit=time_limit,mem_limit=mem_limit)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self,id):
        self.__id = id

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self,title):
        self.__title = title

    @property
    def create_by(self):
        return self.__create_by

    @create_by.setter
    def create_by(self,create_by):
        self.__create_by = create_by

    @property
    def time_limit(self):
        return self.__time_limit

    @time_limit.setter
    def time_limit(self,time_limit):
        self.__time_limit = time_limit
    
    @property
    def mem_limit(self):
        return self.__mem_limit

    @mem_limit.setter
    def mem_limit(self,mem_limit):
        self.__mem_limit = mem_limit
    