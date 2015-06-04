#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 mlckq <moon5ckq@gmail.com>
#
# Distributed under terms of the MIT license.

"""
generate a random list for student register
"""

import sys, random

p = [u"河北省",u"山西省",u"辽宁省",u"吉林省",u"黑龙江省",u"江苏省",u"浙江省",u"安徽省",u"福建省",u"江西省",u"山东省",u"河南省",u"湖北省",u"湖南省",u"广东省",u"海南省",u"四川省",u"贵州省",u"云南省",u"陕西省",u"甘肃省",u"青海省",u"台湾省",u"内蒙古自治区",u"广西壮族自治区",u"西藏自治区",u"宁夏回族自治区",u"新疆维吾尔自治区",u"香港特别行政区",u"澳门特别行政区"]
n = u"甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥"

if __name__ == '__main__':
    count = int(sys.argv[1])
    for idx in xrange(1, count + 1):
        name = ''.join(random.choice(n) for _ in xrange(4))
        user_id = '2014%.5d' % idx
        idcard = '1234567890%.8d' % idx
        pro = random.choice(p)
        tim = random.choice(['1401', '1402', '1501', '1502'])

        exam_range = random.choice(['1-10', '11-20', '20-30'])
        seat_range = '1-30'

        print ('%s,%s,%s,%s,%s,%s,%s' % (name,\
            user_id, idcard, pro, tim, exam_range, seat_range)).encode('utf-8')
