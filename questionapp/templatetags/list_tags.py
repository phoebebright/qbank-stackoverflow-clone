from django import template

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, '__iter__') and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def batch_size(items, size):
    return [items[i:i+size] for i in xrange(0, len(items), size)]

def batches(items, number):
   
    div, mod= divmod(len(items), number)
    if div > 1:
        if mod:
            div += 1
        return batch_size(items, div)
    else:
        if not div:
            return [[item] for item in items] + [[]] * (number - mod)
        elif div == 1 and not mod:
            return [[item] for item in items]
        else:
            # mod now tells you how many lists of 2 you can fit in
            return ([items[i*2:(i*2)+2] for i in xrange(0, mod)] +
                    [[item] for item in items[mod*2:]])

register = template.Library()

@register.filter
def in_batches_of_size(items, size):
    return batch_size(items, int(size))

@register.filter
def in_batches(items, number):
    return batches(items, int(number))
