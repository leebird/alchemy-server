import csv
from django.http import StreamingHttpResponse
from .search_view import SearchView

class DownloadView(SearchView):
    # download function
    view_name = 'download'

    class Echo:
        def write(self, value):
            """Write the value by returning it, instead of storing in a buffer."""
            return value

    def filter_rows(self, rows):
        high_rows = []
        low_rows = []
        gene_file = open('/home/leebird/Dropbox/miRTex paper/use case/tnbc_down_genes.txt','r')
        gene_names = gene_file.read().strip().split('\n')

        for row in rows[1:]:
            if row[0] == '24817091':
                continue

            if row[2].upper() in gene_names:
                row = list(row)
                row[2] = row[2].upper()
                high_rows.append(tuple(row))
            else:
                low_rows.append(row)
        high_rows = sorted(high_rows, key=lambda a:a[2])
        return [rows[0]]+high_rows+low_rows



    def get(self, request, query, dtype):
        self.dtype = int(dtype)
        super(DownloadView, self).get(request, query)
        pseudo_buffer = self.Echo()
        writer = csv.writer(pseudo_buffer)

        rows = self.build_rows()

        rows = self.filter_rows(rows)

        response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="result.csv"'
        return response

    def build_rows(self):
        rows = [('PMID', 'miRNA', 'Gene', 'Directness', 'Sentence')]
        if self.dtype == 1:
            tuples = self.tuples
        elif self.dtype == 2:
            tuples = [row for row in self.tuples if row[3] == 'D']
        elif self.dtype == 3:
            tuples = [row for row in self.tuples if row[3] == 'U']
        else:
            tuples = []

        for row in tuples:
            direct = 'unknown'
            if row[3] == 'D':
                direct = 'direct'

            sents = set()
            for rel_id in row[4].split(','):
                sent_ids = self.rel_sentids[int(rel_id)]
                for sent_id in sent_ids:
                    sents.add(self.sentid_sent[sent_id])

            sents = sorted(list(sents),key=lambda a:a[0])
            sentsText = ' '.join([sent[1] for sent in sents])

            rows.append(row[:3]+(direct,sentsText))

        return rows
