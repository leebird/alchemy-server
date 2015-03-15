import functools

class SpanTagger:
    
    tagHead = u'<{0} class="{1}" style="{2}">'
    tagTail = u'</{0}>'

    @classmethod
    def entity_order(cls, a, b):
        if a.start > b.start:
            return 1
        elif a.start < b.start:
            return -1
        else:
            return int(b.end - a.end)

    @classmethod
    def tag(cls, text, entities, tags, classes, styles):
        pos2head = {}
        pos2tail = {}
        entities = sorted(entities,key=functools.cmp_to_key(cls.entity_order))
                          # cmp=cls.entity_order)

        for entity in entities:

            try:
                htmltag = tags[entity.category]
            except KeyError:
                htmltag = 'span'

            try:
                spancls = classes[entity.category]
            except KeyError:
                spancls = entity.category

            try:
                style = styles[entity.category]
                css = ''
                for cssName, cssVal in style:
                    css += cssName+':'+cssVal+';'
            except KeyError:
                css = ''

            start = entity.start
            end = entity.end

            try:
                pos2head[start].append(cls.tagHead.format(htmltag,spancls,css))
            except KeyError:
                pos2head[start] = [cls.tagHead.format(htmltag,spancls,css)]
            try:
                pos2tail[end].append(cls.tagTail.format(htmltag))
            except KeyError:
                pos2tail[end] = [cls.tagTail.format(htmltag)]

        positions = list(set(list(pos2head.keys()) + list(pos2tail.keys())))
        positions.sort()

        slices = []
        prev = 0        
        
        for p in positions:
            slices.append(text[prev:p])
            tags = []

            if p in pos2tail:
                tags += pos2tail[p]
            if p in pos2head:
                tags += pos2head[p]

            slices += tags

            prev = p
        
        slices.append(text[prev:])

        return ''.join(slices)
        
            
