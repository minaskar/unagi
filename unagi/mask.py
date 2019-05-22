#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Deal with the mask plane of HSC images."""

import numpy as np

from astropy.table import Table

from matplotlib import colors

__all__ = ['Mask', 'BitMasks', 'S18A_BITMASKS', 'PDR1_BITMASKS']

class BitMasks():
    """
    Class for defining HSC bitmasks.
    """

    def __init__(self, data_release='s18a'):
        """
        Define the bitmask plane of HSC coadd image.
        """
        if data_release == 's18a':
            self.bitmasks = S18A_BITMASKS
        elif data_release == 'pdr1':
            self.bitmasks = PDR1_BITMASKS
        else:
            raise NotImplementedError(
                "# Rerun {0} is not available yet".format(data_release))

    def bits2name(self, idx):
        """
        Convert the bit value to the name of the mask plane.
        """
        return self.bitmasks[self.bitmasks['bits'] == idx]['name'][0]

    def name2bits(self, name):
        """
        Convert the name of the mask plane to bits value.
        """
        return self.bitmasks[self.bitmasks['name'] == name.strip().upper()]['bits'][0]

    def get_index(self, name_or_bit):
        """
        Get the index of the mask plane.
        """
        if isinstance(name_or_bit, str):
            flag = self.bitmasks['name'] == name_or_bit.strip().upper()
        else:
            flag = self.bitmasks['bits'] == name_or_bit

        return np.where(flag)[0][0]

    def get_color(self, name_or_bit):
        """
        Return the color string used for displaying the mask plane.
        """
        return self.bitmasks[self.get_index(name_or_bit)]['color']

    def to_table(self):
        """
        Convert the bitmask structured array into astropy table.
        """
        return Table(self.bitmasks)

    def show_table(self):
        """
        Display the bitmask table.
        """
        try:
            _ = get_ipython
            return Table(self.bitmasks).show_in_notebook()
        except NameError:
            return Table(self.bitmasks).show_in_browser()


class Mask():
    """
    Class for HSC mask plane.
    """

    def __init__(self, mask, wcs=None, data_release='s18a'):
        """
        Initialize a HSC mask plane object.

        Parameters:
        -----------
        mask: numpy.ndarray
            2-D bitmask plane from HSC image.
        """
        self.mask = mask.astype(np.uint16)

        # Shape of the array
        h, w = self.mask.shape
        self.height = h
        self.width = w

        # Decode the bitmask array
        self.mask_decode = self.decode(self.mask)

        # Number of available mask planes
        self.n_mask = self.mask_decode.shape[2]

        # WCS information
        self.wcs = wcs

        # Table for bitmask planes
        self.data_release = data_release
        self.table = BitMasks(data_release=self.data_release)

    def decode(self, bitmask):
        '''
        Convert HSC binary mask to a 3-D array,
        with binary digits located in the third axis.

        Parameters:
        -----------
        bin_msk: 2-D np.array, can be loaded from HSC image cutouts

        The code is based on convert_HSC_binary_mask() function by Jia-Xuan Li
        see: https://github.com/AstroJacobLi/slug/blob/master/slug/imutils.py
        '''
        temp = np.array(np.hsplit(np.unpackbits(bitmask.view(np.uint8), axis=1), self.width))

        decode_mask = np.flip(np.transpose(
            np.concatenate(np.flip(np.array(np.dsplit(temp, 2)), axis=0), axis=2),
            axes=(1, 0, 2)), axis=2)

        return decode_mask

    def mask_cmap(self, name_or_bit):
        """
        Get the colormap to show the mask plane.
        """
        return colors.ListedColormap(
            ['white', self.table.get_color(name_or_bit)])

    def extract(self, name_or_bit, show=False):
        """
        Get the 2-D array of one mask plane.
        """
        if show:
            return self.mask_decode[:, :, self.table.get_index(name_or_bit)].astype(np.uint16)
        return self.mask_decode[:, :, self.table.get_index(name_or_bit)]


S18A_BITMASKS = np.array(
    [(0, 'BAD',
      'Bad pixel',
      'red'),
     (1, 'SAT',
      'Source footprint includes saturated pixels',
      'tab:purple'),
     (2, 'INTRP',
      'Source footprint includes interpolated pixels',
      'tab:orange'),
     (3, 'CR',
      'Source footprint includes suspected CR pixels',
      'tab:pink'),
     (4, 'EDGE',
      'Source is close to the edge of the CCD',
      'tab:olive'),
     (5, 'DETECTED',
      'Pixel with detection above the threshold',
      'tab:blue'),
     (6, 'DETECTED_NEGATIVE',
      'Pixel in footprint that is detected as a negative object',
      'gray'),
     (7, 'SUSPECT',
      'Source footprint includes suspect pixels',
      'orangered'),
     (8, 'NO_DATA',
      'No useful data',
      'black'),
     (9, 'BRIGHT_OBJECT',
      'Bright star mask',
      'tab:brown'),
     (10, 'CROSSTALK',
      'Crosstalk',
      'rosybrown'),
     (11, 'NOT_DEBLENDED',
      'Pixel in footprint that is too large to deblend',
      'teal'),
     (12, 'UNMASKEDNAN',
      'NaN pixels that are interpolated over',
      'darkgreen'),
     (13, 'REJECTED',
      'Rejected due to a mask other than EDGE, NO_DATA, or CLIPPED',
      'violet'),
     (14, 'CLIPPED',
      'Pixel that has been clipped',
      'crimson'),
     (15, 'SENSOR_EDGE',
      'Pixel close to the edge of CCD sensor',
      'tab:olive'),
     (16, 'INEXACT_PSF',
      'PSF is not correct',
      'gold')],
    dtype=[('bits', np.uint8), ('name', '<U10'),
           ('meaning', '<U80'), ('color', '<U10')])

PDR1_BITMASKS = np.array(
    [(0, 'BAD',
      'Bad pixel',
      'red'),
     (1, 'SAT',
      'Source footprint includes saturated pixels',
      'tab:purple'),
     (2, 'INTRP',
      'Source footprint includes interpolated pixels',
      'tab:orange'),
     (3, 'CR',
      'Source footprint includes suspected CR pixels',
      'tab:pink'),
     (4, 'EDGE',
      'Source is close to the edge of the CCD',
      'tab:olive'),
     (5, 'DETECTED',
      'Pixel with detection above the threshold',
      'tab:blue'),
     (6, 'DETECTED_NEGATIVE',
      'Pixel in footprint that is detected as a negative object',
      'gray'),
     (7, 'SUSPECT',
      'Source footprint includes suspect pixels',
      'orangered'),
     (8, 'NO_DATA',
      'No useful data',
      'black'),
     (9, 'BRIGHT_OBJECT',
      'Bright star mask',
      'tab:brown'),
     (10, 'CROSSTALK',
      'Crosstalk',
      'rosybrown'),
     (11, 'NOT_DEBLENDED',
      'Pixel in footprint that is too large to deblend',
      'teal'),
     (12, 'UNMASKEDNAN',
      'NaN pixels that are interpolated over',
      'darkgreen'),
     (13, 'CLIPPED',
      'Pixel that has been clipped',
      'crimson')],
    dtype=[('bits', np.uint8), ('name', '<U10'),
           ('meaning', '<U80'), ('color', '<U10')])