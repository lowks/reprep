import numpy
from numpy import maximum, minimum, zeros
from reprep.graphics.numpy_utils import assert_finite, gt, require_shape


def skim_top(a, top_percent):
    ''' Cuts off the top percentile '''
    assert top_percent >= 0 and top_percent < 90
    from scipy import stats
    
    threshold = stats.scoreatpercentile(a.flat, 100 - top_percent) 
    return numpy.minimum(a, threshold)
    

def posneg(value, max_value=None, skim=0):
    """ Converts a 2D value to normalized uint8 RGB red=positive, blue=negative 0-255
     
    """
    assert skim >= 0 and skim < 90
    assert_finite(value)
    value = value.squeeze()
    require_shape((gt(0), gt(0)), value)
    
    if max_value is None:
        abs_value = abs(value)
        if skim != 0:
            abs_value = skim_top(abs_value, skim)
            
        max_value = numpy.max(abs_value)
        if max_value == 0:
            result = zeros((value.shape[0], value.shape[1], 3), dtype='uint8')
            return result

#            raise ValueError('You asked to normalize a matrix which is all 0')

    positive = minimum(maximum(value, 0), max_value) / max_value
    negative = maximum(minimum(value, 0), -max_value) / -max_value

    positive_part = (positive * 255).astype('uint8')
    negative_part = (negative * 255).astype('uint8')
    result = zeros((value.shape[0], value.shape[1], 3), dtype='uint8')
    
    anysign = maximum(positive_part, negative_part)
    result[:, :, 0] = 255 - negative_part[:, :]
    result[:, :, 1] = 255 - anysign
    result[:, :, 2] = 255 - positive_part[:, :]
    
    return result
 
 