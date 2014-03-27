#!/usr/bin/env python
#
# Create a frame of segment-level translation 
#
#
#
import sys
import codecs
import json
import os
from os.path import basename
from collections import namedtuple,defaultdict,Counter
import imt_utils

stderr = lambda x:sys.stderr.write(str(x) + os.linesep)

OutputRow = namedtuple('OutputRow', 'time last_time username user_resident_of user_mt_opinion user_gender interface doc_id segment_id src_len order genre')

# TODO: remove. Hack for the pilot study.
USER_TO_GENDER = {'subject0':'m', 'subject1':'f', 'subject2':'f', 'subject3':'m' }

args = sys.argv[1:]
if len(args) != 2:
    stderr('Usage: python %s dump_file out_file' % (basename(sys.argv[0])))
    sys.exit(-1)
    
dump_file = args[0]
out_file_name = args[1]
dump_row_list = imt_utils.load_middleware_dump(dump_file)
output_row_list = []
total_translation_time = Counter()
user_order_to_time = defaultdict(list)
for i,row in enumerate(dump_row_list):
    if i > 0 and i % 10 == 0:
        sys.stdout.write('.')
        if i % 800 == 0:
            print
    tgt_text_dict = json.loads(row.text)
    segment_to_tgt_txt = imt_utils.final_translations_from_dict(tgt_text_dict)
    doc_name = imt_utils.url2doc(row.src_doc)
    log = json.loads(row.log)
    segment_to_time = imt_utils.segment_times_from_log(log)
    segment_to_mt = imt_utils.initial_translations_from_imt_log(log) if row.interface == 'imt' else imt_utils.initial_translations_from_pe_log(log)
    segment_to_src_txt = imt_utils.source_segments_from_log(log)
    doc_name = imt_utils.url2doc(row.src_doc)
    doc_genre = imt_utils.genre_from_url(row.src_doc)
    for line_id in sorted(segment_to_tgt_txt.keys()):
        segment_id = '%s:%d' % (doc_name, line_id)
        time = segment_to_time[line_id]
        total_translation_time[row.username] += time
        order = int(row.order)
        time_key = '%s:%d' % (row.username,order)
        user_order_to_time[time_key].append(time)
        output_row = OutputRow(time=str(time),
                               last_time=str(0.01),
                               username=row.username,
                               user_resident_of=row.resident_of,
                               user_mt_opinion=row.mt_opinion,
                               user_gender=USER_TO_GENDER[row.username],
                               interface=row.interface,
                               doc_id=doc_name,
                               segment_id=segment_id,
                               src_len=str(len(segment_to_src_txt[line_id].split())),
                               order=str(order),
                               genre=doc_genre)
        output_row_list.append(output_row)

# Fill in the previous time column
for i in xrange(len(output_row_list)):
    row = output_row_list[i]
    order = int(row.order)
    time_key = '%s:%d' % (row.username,order)
    doc_name,line_id = row.segment_id.split(':')
    prev_line_id = int(line_id) - 1
    if prev_line_id >= 0:
        last_time = user_order_to_time[time_key][prev_line_id] + 0.0001
        output_row_list[i] = row._replace(last_time=str(last_time))
    else:
        # Look back to previous document
        time_key = '%s:%d' % (row.username,order-1)
        if time_key in user_order_to_time:
            last_time = user_order_to_time[time_key][-1] + 0.0001
            output_row_list[i] = row._replace(last_time=str(last_time))
        else:
            # This is the first segment
            pass
    
print
print 'Writing to:',out_file_name
imt_utils.write_rows_to_csv(output_row_list, out_file_name)

print
print 'Total translation time'
for username in sorted(total_translation_time.keys()):
    print username,total_translation_time[username]