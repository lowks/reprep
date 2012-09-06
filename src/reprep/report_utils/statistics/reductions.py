from . import np, contract
from reprep.report_utils.statistics import RepRepStats
from scipy.stats.stats import nanmean, nanstd
     

@RepRepStats.reduction
def all(x): #@ReservedAssignment
    """ %s := %s """
    return x

@RepRepStats.reduction
def num(x): #@ReservedAssignment
    """ n%s := Number of samples of %s"""
    return len(x)

@RepRepStats.reduction
def min(x): #@ReservedAssignment
    """ min(%s) := Minimum of %s """
    return np.nanmin(x)

@RepRepStats.reduction
def max(x): #@ReservedAssignment
    """ max(%s) := Maximum of %s """
    return np.nanmax(x)

@RepRepStats.reduction
def mean(x):
    """ E\{%s\} := Average %s """
    return nanmean(x)

@RepRepStats.reduction
def stddev(x):
    """ std\{%s\} := Standard deviation of %s """
    return nanstd(x)

@RepRepStats.reduction
@contract(a='array[N]', returns='tuple(number, number)')
def mean_std(a):
    """ mean,std\{%s\} := mean and standard deviation of %s """
    a = np.array(a)
    return (np.mean(a), np.std(a))

@RepRepStats.reduction
@contract(a='array[N]', returns='tuple(number, number, number)')
def min_mean_max(a):
    """ b\{%s\} := Min, mean and max of %s """
    a = np.array(a)
    return (np.nanmin(a), nanmean(a), np.max(a))


@RepRepStats.reduction_display
@contract(s='tuple(number, number)', returns='str')
def mean_std_display(s):
    mean, std = s
    return '%s +/- %s' % (mean, std)

@RepRepStats.reduction_display
@contract(s='tuple(number, number, number)', returns='str')
def min_mean_max_s(s):
    a, b, c = s
    return '(%s) %s (%s)' % (a, b, c)


@RepRepStats.reduction_display
def string(s):
    return str(s)


@RepRepStats.reduction_display
def f(s):
    """ Format as a float number ('f' formatter) """
    return '%f' % s

@RepRepStats.reduction_display
def perc(s):
    """ Format as a percentual """ 
    return '%d%%' % (100 * s)

@RepRepStats.reduction_display
def g(s):
    """ Format as a float number ('g' formatter) """
    return '%g' % s

@RepRepStats.reduction_display
def d(s):
    """ Format as an integer ('d' formatter) """
    return '%d' % s

