import pandas as pd
import pingouin as pg
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import seaborn as sns
import matplotlib.pyplot as plt

le = LabelEncoder()
mscaler = MinMaxScaler()

# # settings to try and standardize plots
# plot_settings = {'ytick.labelsize': 16,
#                         'xtick.labelsize': 16,
#                         'font.size': 22,
#                         'figure.figsize': (10, 5),
#                         'axes.titlesize': 22,
#                         'axes.labelsize': 18,
#                         'lines.linewidth': 2,
#                         'lines.markersize': 3,
#                         'legend.fontsize': 11,
#                         'mathtext.fontset': 'stix',
#                         'font.family': 'STIXGeneral'}

def get_rm_plot(df, subj, betw, within, outfold, repl=False):
    """
    Get repeated measures ANOVAs and plot descriptive means.
    `df`        - the pandas dataframe
    `subj`      - the individual observations
    `betw`      - the between subjects factors (dv)
    `within`    - the within subjects factors (iv)
    `outfold`   - the folder for output
    `repl`      - whether to replace the output files
    """
    # conduct paired ttests to ID length of nouns/verbs within lgs according to word order
    v1 = df[df[betw]=='VS']
    v1ttest = pg.ttest(v1[within[0]], v1[within[1]], paired=True).round(3)
    n1 = df[df[betw]=='SV']
    n1ttest = pg.ttest(n1[within[0]], n1[within[1]], paired=True).round(3)
    free = df[df[betw]=='free']
    # print(free)
    try:
        freettest = pg.ttest(free[within[0]], free[within[1]], paired=True).round(3)
    except:
        freettest = ""

    # reduce dataset to only comparisons for word class length
    # creates a 'value' column with the length variables and a 'variable' column
    # with the within-subjects classes
    df = pd.melt(df, id_vars=[subj, betw], value_vars=within)
    if '_freq' in within[0] and '_freq' not in within[1]:
        rpldict = {"_": " ", "Vlen": "Verbs", "Nlen": "Nouns", "Pronlen": "Pronouns", "Arglen": "Arguments", "Predlen": "Predicates"}
        wn0 = within[0]
        wn1 = within[1]
        for k in rpldict.keys():
            wn0 = wn0.replace(k, rpldict[k])
            wn1 = wn1.replace(k, rpldict[k])
        df = df.replace({'variable': {within[0]: wn0, within[1]: wn1}})
    elif 'Arg' in within[0]:
        df = df.replace({'variable': {within[0]: 'Arguments', within[1]: 'Predicates'}})
    elif 'Pron' in within[0]:
        df = df.replace({'variable': {within[0]: 'Pronouns', within[1]: 'Verbs'}})
    else:
        df = df.replace({'variable': {within[0]: 'Nouns', within[1]: 'Verbs'}})
    df = df.rename(columns={"variable": "Word lengths"})
    # conduct a repeated measures anova comparing lengths
    aov = pg.rm_anova(data=df, dv='value', within='Word lengths', subject=subj).round(3)
    # conduct a mixed anova with word order as between-subjects variable
    maov = pg.mixed_anova(data=df, dv='value', between=betw, within='Word lengths', subject=subj).round(3)

    posthoc = pg.pairwise_tests(data=df, dv='value', between=betw, within='Word lengths', subject=subj).round(3)
    #df.pairwise_tests(dv='value', between=betw, within='word lengths').round(3)
    # print(posthoc)
    if repl:
        with open(outfold+"means-"+"_".join(within)+"_posthoc.txt", "w") as f:
            f.write(posthoc.to_string(header=True, index=False))
            f.write("\n\nVS Languages mean Noun vs Verb lengths\n")
            f.write(v1ttest.to_string(header=True, index=False))
            f.write("\n\nSV Languages mean Noun vs Verb lengths\n")
            f.write(n1ttest.to_string(header=True, index=False))
            f.write("\n\nFree Languages mean Noun vs Verb lengths\n")
            f.write(freettest.to_string(header=True, index=False))
        # print()

        # Set the overall style and context for journal publication
        sns.set_theme(style="ticks", context="paper", font_scale=1.5, palette="colorblind")
        # plot the data
        ax = sns.pointplot(data=df, x='Word lengths', y='value', hue=betw, dodge=True, capsize=.05, errorbar='se')
        _ = plt.title('Mean lengths by word class')
        # plt.style.use(plot_settings)
        sns.move_legend(ax, "upper left")#, bbox_to_anchor=(1, 1))
        plt.tight_layout()
        plt.savefig(outfold+"means-"+"_".join(within)+"_plot.png", dpi=300, bbox_inches='tight')
        plt.clf()

def get_anova_wordorder(df, subj, betw, within, outfold, ds, repl=False):
    # reduce dataset to only comparisons for word order and N1 ratio
    df = df[[subj, betw, within]]
    # conduct a one-way anova comparing word order and N1 ratio
    aov = pg.anova(data=df, dv=within, between=betw).round(3)
    if len(df[betw].value_counts().keys()) > 3:
        orders = ['VI', 'VM', 'VF', 'free']
    else:
        orders = ['SV', 'VS', 'free']

    posthoc = pg.pairwise_tests(data=df, dv=within, between=betw, subject=subj).round(3)
    # print(posthoc)
    if repl:
        if len(orders) > 3:
            with open(outfold+ds+"_"+within+"_posthoc.txt", "w") as f:
                f.write(posthoc.to_string(header=True, index=False))
        else:
            with open(outfold+within+"_"+ds+"_posthoc.txt", "w") as f:
                f.write(posthoc.to_string(header=True, index=False))
    # print()

    # Set the overall style and context for journal publication
    sns.set_theme(style="ticks", context="paper", font_scale=1.5, palette="colorblind")
    # plot the data
    ax = sns.pointplot(data=df, x=betw, y=within, hue=betw, dodge=True, capsize=.05, errorbar='se', order=orders)
    # plt.ylim(3.5, 8)
    if ds == 'Trans_order':
        _ = plt.title('Transitive word order proportions'.format())
    else:
        _ = plt.title('N1 ratio and word order ({source})'.format(source=ds))
    if betw == 'Noun_Verb_order':
        ax.set_xlabel('Intransitive order')
    ax.set_ylabel('N1 ratio')
    # plt.style.use(plot_settings)
    # sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    if repl:
        if len(orders) > 3:
            plt.savefig(outfold+ds+"_"+within+".png", dpi=300, bbox_inches='tight')
        else:
            plt.savefig(outfold+within+"_"+ds+".png", dpi=300, bbox_inches='tight')
    plt.clf()

def wordord_linear_model(df, dv, iv, groups, plotres=False):
    """
    A function to run a linear mixed effects model on a dataframe.
    `df`        - pandas dataframe
    `dv`        - the dependent variable (str), assumed to be categorical
    `iv`        - the independent variable(s) (str or list of str), must be continuous (scaled)
    `groups`    - the grouping factors (str or list of str), assumed to be categorical
    `plotres`   - whether to plot residuals
    """
    # check if the iv is a string, if so make it a list
    if isinstance(iv, str):
        iv = [iv]
    # check if the groups variable is a string, if so make it a list
    if isinstance(groups, str):
        groups = [groups]
    # transform the dependent variable to numeric
    cat_cols = [dv]
    df[cat_cols] = df[cat_cols].apply(le.fit_transform)
    # we assume the ivs are continous and scaled, but they can be rescaled here if necessary
    # df[iv] = mscaler.fit_transform(df[iv]) # scale
    ivstring = "+".join(iv) # in case we have multiple ivs
    # print(ivstring)
    formula = f'{dv} ~ {ivstring}' # final formula
    # assume we should model the groups as random effects if there are multiple
    if len(groups) > 1:
        # instantiate a dict for our mixed effects
        vc_form = {g: f"0 + C({g})" for g in groups}
        df['group'] = 1 # set group to `1` in order to model multiple random effects
        model = smf.mixedlm(formula, df,
                            groups=df['group'],
                            vc_formula=vc_form,
                            )
    else:
        # otherwise set group to the first item in the groups list
        df['group'] = df[groups[0]]
        model = smf.mixedlm(formula, df,
                            groups=df['group'],
                            )

    result = model.fit() # run the model

    # check whether to plot residuals
    if plotres:
        # Get residuals
        residuals = result.resid
        # Q-Q plot for normality
        from scipy import stats
        stats.probplot(residuals, dist="norm", plot=plt)
        plt.title(f"Residual Q-Q Plot {group}: {n}")
        plt.show()
        # Plot residuals vs fitted values
        fitted = result.fittedvalues
        plt.scatter(fitted, residuals)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.xlabel(f"Fitted Values")
        plt.ylabel(f"Residuals")
        plt.title(f"Residual Plot {group}: {n}")
        plt.show()

    return result

def resultsdict(df, dv, iv, group, result):
    """
    A function to get results from a series of mixed effects models.
    `dv`        - the dependent variable (str)
    `iv`        - the independent variable (str)
    `group`     - the grouping variable (str)
    `result`    - the output from the linear model (via statsmodels.formula.api [smf])
    """
    tdict = {'dv': dv, 'iv': iv, 'group': group, 'macros': ", ".join([k for k in df['macroarea'].value_counts().keys()])}
    # go through each table of results
    for num, tab in enumerate(result.tables):
        # get the table as a dict and store results in our master table
        dtab = tab.to_dict()
        if 0 in dtab.keys():
            df1 = tab.set_index(0)[1].to_dict()
            df2 = tab.set_index(2)[3].to_dict()
            for k, v in df1.items():
                tdict[k] = v
            for k, v in df2.items():
                tdict[k] = v
        # ignore table entries without zero index
        else:
            for k in dtab.keys():
                tdict[k] = dtab[k][iv]
    return tdict

def run_mixed(df, dv, ivslist, groups, ranges, gcounts):
    """
    Get a series of results from a mixed effects model
    `df`        - the dataframe
    `dv`        - the dependent variable (categorical)
    `ivslist`   - the list of independent variables (will be examined individually)
    `groups`    - a list of groups (categorical)
    `ranges`    - a range of numbers representing minimum group sizes
    `gcounts`   - a dict of groups and number of observations found in the dataset
    """
    mcount = 0 # count the model number
    finaldict = {} # empty dict to store all results
    # first go through all the independent variables
    for iv in ivslist:
        # for each number in the range
        for n in ranges:
            greater = [k for k, v in gcounts.items() if v > n] # select groups with more than the number
            df2 = df[df['Family_line'].isin(greater)] # only get members of those groups
            # print(len(df2))
            result = wordord_linear_model(df2, dv, iv, groups) # run the linear model
            sumdf = result.summary() # get the summary
            # print(sumdf)
            finaldict[mcount] = resultsdict(df2, dv, iv, groups, sumdf) # get the results
            finaldict[mcount]['range'] = str(max(df2[iv]))+" > "+str(min(df2[iv]))
            # print(finaldict[mcount])
            mcount += 1
    # some renaming for columns
    finalcols = ['iv', 'No. Observations:', 'Coef.', 'Std.Err.', 'z', 'P>|z|', 'Converged:', 'No. Groups:', 'Min. group size:', 'Max. group size:', 'range']
    df3 = pd.DataFrame.from_dict(finaldict, orient='index')
    df3 = df3[finalcols]
    df3 = df3.rename(columns={'No. Observations:': 'NumLangs'})
    idnames = ['NumLangs', 'iv']
    # here we restack to have results per number of languages in columns
    # and features (ivs) as the index column
    df3 = df3.set_index(idnames).stack().unstack('iv').T
    return df3
