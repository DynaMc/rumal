import pyparsing
from django.db.models import Q


class Node(list):
        def __eq__(self, other):
                return list.__eq__(self, other) and self.__class__ == other.__class__

        def __repr__(self):
                return '%s(%s)' % (self.__class__.__name__, list.__repr__(self))

        @classmethod
        def group(cls, expr):
                def group_action(s, l, t):
                        try:
                                lst = t[0].asList()
                        except (IndexError, AttributeError), e:
                                lst = t
                        return [cls(lst)]

                return pyparsing.Group(expr).setParseAction(group_action)

        def get_query(self):
                raise NotImplementedError()


class ComparisonNode(Node): pass
class AndNode(Node): pass
class OrNode(Node): pass
class NotNode(Node): pass


# GRAMMAR
not_operator        = pyparsing.oneOf(['not', '^'], caseless=True)
and_operator        = pyparsing.oneOf(['and', '&'], caseless=True)
or_operator         = pyparsing.oneOf(['or', '|'], caseless=True)

ident = pyparsing.Word(pyparsing.alphanums+'.'+'/'+':'+'_'+'-').setParseAction(lambda t: t[0].replace('_', ' '))

equal_exact = pyparsing.Keyword('==', caseless=True)
equal_contains = pyparsing.Keyword('=', caseless=True).setParseAction(lambda t: '$regex')
regex = pyparsing.Keyword('~', caseless=True).setParseAction(lambda t: '$regex')
greater_than_equal = pyparsing.Keyword('$gte', caseless=True)
greater_than = pyparsing.Keyword('$gt', caseless=True)
lower_than_equal = pyparsing.Keyword('$lte', caseless=True)
lower_than = pyparsing.Keyword('$lt', caseless=True)

comparison_list = ['$gte', '$gt', '$lte', '$lt', '$regex']
comparison_operator = equal_exact | equal_contains | regex |\
                      greater_than_equal | greater_than | lower_than_equal | lower_than


keyword = pyparsing.Keyword('url', caseless=True) | \
          pyparsing.Keyword('id', caseless=True).setParseAction(lambda t: 'frontend_id') | \
          pyparsing.Keyword('timestamp', caseless=True) | \
          pyparsing.Keyword('urls', caseless=True).setParseAction(lambda t: 'url_map.url')

integer = pyparsing.Regex(r'[+-]?\d+').setParseAction(lambda t: int(t[0]))
float_ = pyparsing.Regex(r'[+-]?\d+\.\d*').setParseAction(lambda t: float(t[0]))

quote = pyparsing.QuotedString('"')

literal_true = pyparsing.Keyword('true', caseless=True)
literal_false = pyparsing.Keyword('false', caseless=True)
boolean_literal = literal_true | literal_false

comparison_operand = quote | ident | float_ | integer
comparison_expr = ComparisonNode.group(keyword + comparison_operator + comparison_operand)


boolean_expr = pyparsing.operatorPrecedence(
    comparison_expr | boolean_literal,
    [
        (NotNode.group(not_operator), 1, pyparsing.opAssoc.RIGHT),
        (AndNode.group(and_operator), 2, pyparsing.opAssoc.LEFT),
        (OrNode.group(or_operator),  2, pyparsing.opAssoc.LEFT),
    ])

grammar = boolean_expr


def search(string):
    """
    Parse tree of advanced search
    :param string:
    :return: AST or false
    """
    try:
        return grammar.parseString(string, parseAll=True)
    except pyparsing.ParseException:
        return False


def get_query(query):
    """
    Builds the query string for mongodb
    :param query: AST
    :return:
    """
    return_query = {}
    iterable = iter(xrange(len(query)))
    for i in iterable:

        if type(query[i]) is pyparsing.ParseResults:
            return_query = get_query(query[i])

        if type(query[i]) is AndNode:
            return_query = {"$and": [return_query, get_element(query[i + 1])]}
            next(iterable)

        if type(query[i]) is OrNode:
            return_query = {"$or": [return_query, get_element(query[i + 1])]}
            next(iterable)

        if type(query[i]) is ComparisonNode:
            # greater than or equal comparison can be used for timestamps
            if query[i][1] in comparison_list:
                return_query.update({query[i][0]: {query[i][1]: query[i][2]}})

            else:
                return_query.update({query[i][0]: query[i][2]})

    return return_query


def get_element(element):
    """
    get_query helper function
    :param element: element from AST
    :return:
    """
    if type(element) is ComparisonNode:

        if element[1] in comparison_list:
            return {element[0]: {element[1]: element[2]}}

        return {element[0]: element[2]}

    if type(element) is pyparsing.ParseResults:
        return get_query(element)

