import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
import pandas as pd
import numpy as np
rcParams['font.size'] = 24
sns.set_style("whitegrid")

from scipy.stats import iqr, mannwhitneyu, ttest_ind, normaltest

import pandas as pd
import numpy as np

from statsmodels.formula.api import ols

def multiple_linear_regression(formula, df, show_summary=False):
    print '\n' + formula
    lm = ols(formula=formula, data = df).fit()
    print '\t R2=' + str(lm.rsquared)
    if show_summary:
        print lm.summary()

def clean_csv(path_brain, path_sc):
    df_brain = pd.read_csv(path_brain)
    df_sc = pd.read_csv(path_sc)
    
    df_brain = df_brain.drop([u for u in df_brain.keys() if u.startswith('Unnamed:') or u.startswith('brain segmentation')], axis=1)
    df_sc = df_sc.drop([u for u in df_sc.keys() if u.startswith('Unnamed:') or u.startswith('brain segmentation')], axis=1)
    
    df_brain_sc = pd.merge(df_sc, df_brain, how='inner', on=['subject', 'center', 'age', 'gender', 'phenotype',
                                                             'disease_duration', 'edss_M0', 'edss_py_M0', 'T25FWT_M0', '9HPT_M0',
                                                              'edss_M24', 'edss_py_M24', 'T25FWT_M24', '9HPT_M24'])

    brain_motor_lst = ['brain_' + t + r_l for t in ['M1'] for r_l in ['-R', '-L']]
    brainstem_motor_lst = ['brainstem_' + t + r_l for t in ['CST'] for r_l in ['-R', '-L']]
    sc_motor_lst = ['sc_' + t + r_l for t in ['LCST', 'VCST'] for r_l in ['-R', '-L']]
    brain_motor_ext_lst = brain_motor_lst + ['brain_'+t+r_l for t in ['PMd', 'PMv', 'preSMA', 'SMA', 'S1'] for r_l in ['-R', '-L']]
    
    cns_full_lst = ['brain_full', 'brainstem_full', 'sc_full']
    cns_motor_lst = brain_motor_lst + brainstem_motor_lst + sc_motor_lst
    cns_motor_ext_lst = brain_motor_ext_lst + brainstem_motor_lst + sc_motor_lst

    df_brain_sc['count_cns_full'] = df_brain_sc[['count_'+r for r in cns_full_lst]].sum(axis=1)
    df_brain_sc['tlv_cns_full'] = df_brain_sc[['tlv_'+r for r in cns_full_lst]].sum(axis=1)
    df_brain_sc['vol_cns_full'] = df_brain_sc[['vol_'+r for r in cns_full_lst]].sum(axis=1)
    df_brain_sc['nlv_cns_full'] = df_brain_sc['tlv_cns_full'] / df_brain_sc['vol_cns_full']
    
    df_brain_sc['count_cns_motor'] = df_brain_sc[['count_'+r for r in cns_motor_lst]].sum(axis=1)
    df_brain_sc['alv_cns_motor'] = df_brain_sc[['alv_'+r for r in cns_motor_lst]].sum(axis=1)
    df_brain_sc['vol_cns_motor'] = df_brain_sc[['vol_'+r for r in cns_motor_lst]].sum(axis=1)
    df_brain_sc['nlv_cns_motor'] = df_brain_sc['alv_cns_motor'] / df_brain_sc['vol_cns_motor']
    df_brain_sc['extension_cns_motor'] = df_brain_sc['alv_cns_motor'] / df_brain_sc['tlv_cns_full']
    
    df_brain_sc['count_cns_motor-ext'] = df_brain_sc[['count_'+r for r in cns_motor_ext_lst]].sum(axis=1)
    df_brain_sc['alv_cns_motor-ext'] = df_brain_sc[['alv_'+r for r in cns_motor_ext_lst]].sum(axis=1)
    df_brain_sc['vol_cns_motor-ext'] = df_brain_sc[['vol_'+r for r in cns_motor_ext_lst]].sum(axis=1)
    df_brain_sc['nlv_cns_motor-ext'] = df_brain_sc['alv_cns_motor-ext'] / df_brain_sc['vol_cns_motor-ext']
    df_brain_sc['extension_cns_motor-ext'] = df_brain_sc['alv_cns_motor-ext'] / df_brain_sc['tlv_cns_full']

    df_brain_sc['count_brain_motor'] = df_brain_sc[['count_'+r for r in brain_motor_lst]].sum(axis=1)
    df_brain_sc['alv_brain_motor'] = df_brain_sc[['alv_'+r for r in brain_motor_lst]].sum(axis=1)
    df_brain_sc['vol_brain_motor'] = df_brain_sc[['vol_'+r for r in brain_motor_lst]].sum(axis=1)
    df_brain_sc['nlv_brain_motor'] = df_brain_sc['alv_brain_motor'] / df_brain_sc['vol_brain_motor']
    df_brain_sc['extension_brain_motor'] = df_brain_sc['alv_brain_motor'] / df_brain_sc['tlv_brain_full']

    df_brain_sc['count_brain_motor-ext'] = df_brain_sc[['count_'+r for r in brain_motor_ext_lst]].sum(axis=1)
    df_brain_sc['alv_brain_motor-ext'] = df_brain_sc[['alv_'+r for r in brain_motor_ext_lst]].sum(axis=1)
    df_brain_sc['vol_brain_motor-ext'] = df_brain_sc[['vol_'+r for r in brain_motor_ext_lst]].sum(axis=1)
    df_brain_sc['nlv_brain_motor-ext'] = df_brain_sc['alv_brain_motor-ext'] / df_brain_sc['vol_brain_motor-ext']
    df_brain_sc['extension_brain_motor-ext'] = df_brain_sc['alv_brain_motor-ext'] / df_brain_sc['tlv_brain_full']

    df_brain_sc['count_brainstem_motor'] = df_brain_sc[['count_'+r for r in brainstem_motor_lst]].sum(axis=1)
    df_brain_sc['alv_brainstem_motor'] = df_brain_sc[['alv_'+r for r in brainstem_motor_lst]].sum(axis=1)
    df_brain_sc['vol_brainstem_motor'] = df_brain_sc[['vol_'+r for r in brainstem_motor_lst]].sum(axis=1)
    df_brain_sc['nlv_brainstem_motor'] = df_brain_sc['alv_brainstem_motor'] / df_brain_sc['vol_brainstem_motor']
    df_brain_sc['extension_brainstem_motor'] = df_brain_sc['alv_brainstem_motor'] / df_brain_sc['tlv_brainstem_full']

    df_brain_sc['count_sc_motor'] = df_brain_sc[['count_'+r for r in sc_motor_lst]].sum(axis=1)
    df_brain_sc['alv_sc_motor'] = df_brain_sc[['alv_'+r for r in sc_motor_lst]].sum(axis=1)
    df_brain_sc['vol_sc_motor'] = df_brain_sc[['vol_'+r for r in sc_motor_lst]].sum(axis=1)
    df_brain_sc['nlv_sc_motor'] = df_brain_sc['alv_sc_motor'] / df_brain_sc['vol_sc_motor']
    df_brain_sc['extension_sc_motor'] = df_brain_sc['alv_sc_motor'] / df_brain_sc['tlv_sc_full']

    df_brain_sc['nlv_brain_full'] = df_brain_sc['tlv_brain_full'] / df_brain_sc['vol_brain_full']
    df_brain_sc['nlv_brainstem_full'] = df_brain_sc['tlv_brainstem_full'] / df_brain_sc['vol_brainstem_full']
    df_brain_sc['nlv_sc_full'] = df_brain_sc['tlv_sc_full'] / df_brain_sc['vol_sc_full']

    return df_brain, df_sc, df_brain_sc


def bar_plot(df, total_lst, cst_lst, roi_lst):
    x_lst = range(len(roi_lst))

    total_median = [np.median(df[v].values) for v in total_lst]
    cst_median = [np.median(df[v].values) for v in total_lst]

#     total_iqr = [iqr(df[v].values) for v in total_lst]
#     cst_iqr = [iqr(df[v].values) for v in total_lst]
    fig = plt.figure(figsize=[6, 8])

    # plot
    barWidth = 0.5
    fontsize = 15
    # Create green Bars
    p1 = plt.bar(x_lst, cst_median, color='tomato', edgecolor='white', width=barWidth)#, yerr=cst_iqr)
    # Create orange Bars
    p2 = plt.bar(x_lst, total_median, bottom=cst_median, color='plum', edgecolor='white', width=barWidth)#, yerr=total_iqr)

    # Custom x axis
    plt.xticks(x_lst, roi_lst)
    plt.legend((p1[0], p2[0]), ('Motor', 'Total'), fontsize=fontsize, loc='upper right')
    plt.yticks(size=fontsize)
    plt.xticks(size=fontsize)
#     ax.set_ylabel(y_label, fontsize=fontsize)
#     ax.set_xlabel(x_label, fontsize=fontsize)
    # Show graphic
    plt.show()
    plt.close()

    
def refactor_df(df, x, x_lst, y, h, h_lst):
    df_new = pd.DataFrame(columns=[x, y, h])
    for index, row in df.iterrows():
        for xx in x_lst:
            for hh in h_lst:
                idx_new = len(df_new.index)
                df_new.loc[idx_new, x] = xx
                df_new.loc[idx_new, h] = hh
                val_y = row['_'.join([y, xx, hh])]
                if y == 'nlv':
                    val_y *= 100.
                df_new.loc[idx_new, y] = val_y

    return df_new


def box_plot(df, x, x_label, order_lst, y_label, h, hue_order, fname_out, palette, ylim, plot_type, save_png=False):
    df_ref = refactor_df(df, x, order_lst, y_label, h, hue_order)
    df_ref[y_label] = df_ref[y_label].astype(float)

    fontsize = 20
    fig = plt.figure(figsize=[12, 8])

    if plot_type == 'boxes':
        sns.boxplot(x=x, y=y_label, data=df_ref, hue=h, hue_order=hue_order, order=order_lst, palette=palette)
    else:
        sns.violinplot(x=x, y=y_label, data=df_ref, hue=h, palette=palette, hue_order=hue_order, order=order_lst, scale='area', bw=.3)

    plt.ylim(ylim)
    plt.legend(loc="upper left", fontsize=fontsize)
    plt.yticks(size=fontsize)
    plt.xticks(size=fontsize)
    plt.ylabel(y_label, fontsize=fontsize)
    plt.xlabel(x_label, fontsize=fontsize)
    plt.show()
    
    if save_png:
        fig.savefig(fname_out)
    plt.close()


def print_stats(df, label_info, nb_dec=2):
    vals = df[label_info].dropna().values
    if label_info.startswith('nlv') or label_info.startswith('extension'):
        vals *= 100.
    print label_info
    print '\tMean: '+str(round(np.mean(vals),nb_dec))
    print '\tSD: '+str(round(np.std(vals),nb_dec))
    print '\tMedian: '+str(round(np.median(vals),nb_dec))
    print '\tIQR: '+str(round(iqr(vals),nb_dec))
    print '\tRange: ['+str(round(np.min(vals),nb_dec))+', '+str(round(np.max(vals),nb_dec))+']'
    
def paired_test(df, label1, label2):
    vals1 = df[label1].dropna().values
    vals2 = df[label2].dropna().values
    if normaltest(vals1) < 0.05 or normaltest(vals2) < 0.05:
        _, p = mannwhitneyu(vals1, vals2)
    else:
        _, p = ttest_ind(vals1, vals2)
    print label1+' vs. '+label2
    if p < 0.05:
        print '\t'+str(round(p, 6))
    else:
        print '\tNot Sign.'