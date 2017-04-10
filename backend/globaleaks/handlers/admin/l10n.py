# -*- coding: utf-8 -*-
#
# admin/lang
#  **************
#
# Backend supports for jQuery File Uploader, and implementation of the
# file language statically uploaded by the Admin

# This code differs from handlers/file.py because files here are not tracked in the DB

from __future__ import with_statement

import json

from storm.expr import And
from twisted.internet.defer import inlineCallbacks

from globaleaks.models import CustomTexts
from globaleaks.handlers.base import BaseHandler
from globaleaks.orm import transact
from globaleaks.rest import errors
from globaleaks.rest.apicache import GLApiCache


def db_get_custom_texts(store, tid, lang):
    return CustomTexts.db_get(store, And(CustomTexts.lang == lang,
                                         CustomTexts.tid == tid))


@transact
def get_custom_texts(store, tid, lang):
    try:
        custom_texts = db_get_custom_texts(store, tid, lang)
    except:
        return {}

    return custom_texts.texts


@transact
def update_custom_texts(store, tid, lang, texts):
    try:
        custom_texts = db_get_custom_texts(store, tid, lang)
    except errors.ModelNotFound:
        custom_texts = CustomTexts()
        custom_texts.lang = lang
        custom_texts.tid = tid
        store.add(custom_texts)

    custom_texts.texts= texts


class AdminL10NHandler(BaseHandler):
    @BaseHandler.transport_security_check('admin')
    @BaseHandler.authenticated('admin')
    @inlineCallbacks
    def get(self, lang):
        custom_texts = yield get_custom_texts(self.current_tenant, lang)

        self.write(custom_texts)

    @BaseHandler.transport_security_check('admin')
    @BaseHandler.authenticated('admin')
    @inlineCallbacks
    def put(self, lang):
        request = json.loads(self.request.body)

        yield update_custom_texts(self.current_tenant, lang, request)

        GLApiCache.invalidate(self.current_tenant)

        self.set_status(202)  # Updated

    @BaseHandler.transport_security_check('admin')
    @BaseHandler.authenticated('admin')
    @inlineCallbacks
    def delete(self, lang):
        yield CustomTexts.delete(tid=self.current_tenant, lang=unicode(lang))

        GLApiCache.invalidate(self.current_tenant)
