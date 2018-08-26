from django import template

from OpenBench.models import Test
from OpenBench.utils import ELO

def oneDigitPrecision(value):
    try:
        value = round(value, 1)
        if '.' not in str(value):
            return str(value) + '.0'
        pre, post = str(value).split('.')
        post += '0'
        return pre + '.' + post[0:1]
    except:
        return value

def twoDigitPrecision(value):
    try:
        value = round(value, 2)
        if '.' not in str(value):
            return str(value) + '.00'
        pre, post = str(value).split('.')
        post += '00'
        return pre + '.' + post[0:2]
    except:
        return value

def gitDiffLink(test):

    if type(test) != Test:
        dev     = test['dev']['source']
        base    = test['base']['source']
        devsha  = test['dev']['sha']
        basesha = test['base']['sha']

    else:
        dev     = test.dev.source
        base    = test.base.source
        devsha  = test.dev.sha
        basesha = test.base.sha

    # TODO: Broke when I changed to git clone instead of zipfile
    #repo = '/'.join(dev.split('/')[:-2])
    repo = dev

    return '{0}/compare/{1}...{2}'.format(repo, basesha[:8], devsha[:8])

def shortStatBlock(test):

    lowerllr   = twoDigitPrecision(test.lowerllr)
    currentllr = twoDigitPrecision(test.currentllr)
    upperllr   = twoDigitPrecision(test.upperllr)
    elolower   = twoDigitPrecision(test.elolower)
    eloupper   = twoDigitPrecision(test.eloupper)

    return 'LLR: {0} ({1}, {2}) [{3}, {4}]\n'.format(currentllr, lowerllr, upperllr, elolower, eloupper) \
         + 'Games: {0} W: {1} L: {2} D: {3}'.format(test.games, test.wins, test.losses, test.draws)

def longStatBlock(test):

    tokens = test.devoptions.split(' ')
    threads = tokens[0].split('=')[1]
    network = tokens[1].split('=')[1]

    lower, elo, upper = ELO(test.wins, test.losses, test.draws)
    error = max(upper - elo, elo - lower)

    elo        = twoDigitPrecision(elo)
    error      = twoDigitPrecision(error)
    lowerllr   = twoDigitPrecision(test.lowerllr)
    currentllr = twoDigitPrecision(test.currentllr)
    upperllr   = twoDigitPrecision(test.upperllr)
    elolower   = twoDigitPrecision(test.elolower)
    eloupper   = twoDigitPrecision(test.eloupper)

    return 'ELO   | {0} +- {1} (95%)\n'.format(elo, error) \
         + 'SPRT  | {0}s Threads={1} Network={2}\n'.format(test.timecontrol, threads, network) \
         + 'LLR   | {0} ({1}, {2}) [{3}, {4}]\n'.format(currentllr, lowerllr, upperllr, elolower, eloupper) \
         + 'Games | N: {0} W: {1} L: {2} D: {3}'.format(test.games, test.wins, test.losses, test.draws) \

def testResultColour(test):

    if test.passed: return 'green'
    if test.failed:
        if test.wins >= test.losses: return 'yellow'
        return 'red'
    return ''

register = template.Library()
register.filter('oneDigitPrecision', oneDigitPrecision)
register.filter('twoDigitPrecision', twoDigitPrecision)
register.filter('gitDiffLink', gitDiffLink)
register.filter('shortStatBlock', shortStatBlock)
register.filter('longStatBlock', longStatBlock)
register.filter('testResultColour', testResultColour)

