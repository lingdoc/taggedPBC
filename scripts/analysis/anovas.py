import pandas as pd
import pingouin as pg
import seaborn as sns
import matplotlib.pyplot as plt

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
    # print the comparisons
    # print(within)
    # print(aov)
    # print()
    # conduct a mixed anova with word order as between-subjects variable
    maov = pg.mixed_anova(data=df, dv='value', between=betw, within='Word lengths', subject=subj).round(3)
    # print(maov)
    # print()

    posthoc = pg.pairwise_tests(data=df, dv='value', between=betw, within='Word lengths', subject=subj).round(3)
    #df.pairwise_tests(dv='value', between=betw, within='word lengths').round(3)
    print(posthoc)
    if repl:
        with open(outfold+"means-"+"_".join(within)+"_posthoc.txt", "w") as f:
            f.write(posthoc.to_string(header=True, index=False))
            f.write("\n\nVS Languages mean Noun vs Verb lengths\n")
            f.write(v1ttest.to_string(header=True, index=False))
            f.write("\n\nSV Languages mean Noun vs Verb lengths\n")
            f.write(n1ttest.to_string(header=True, index=False))
            f.write("\n\nFree Languages mean Noun vs Verb lengths\n")
            f.write(freettest.to_string(header=True, index=False))
        print()

        # plot the data
        ax = sns.pointplot(data=df, x='Word lengths', y='value', hue=betw, dodge=True, capsize=.05, errorbar='se', palette=sns.color_palette('bright'))
        _ = plt.title('Mean lengths by word class')
        # plt.style.use(plot_settings)
        sns.move_legend(ax, "upper left")#, bbox_to_anchor=(1, 1))
        plt.tight_layout()
        plt.savefig(outfold+"means-"+"_".join(within)+"_plot.png")
        plt.clf()

def get_anova_wordorder(df, subj, betw, within, outfold, ds, repl=False):
    # reduce dataset to only comparisons for word order and N1 ratio
    df = df[[subj, betw, within]]
    # conduct a one-way anova comparing word order and N1 ratio
    aov = pg.anova(data=df, dv=within, between=betw).round(3)
    # print the comparisons
    # print(within)
    # print(aov)
    # print()
    if len(df[betw].value_counts().keys()) > 3:
        orders = ['VI', 'VM', 'VF', 'free']
    else:
        orders = ['SV', 'VS', 'free']

    posthoc = pg.pairwise_tests(data=df, dv=within, between=betw, subject=subj).round(3)
    print(posthoc)
    if repl:
        if len(orders) > 3:
            with open(outfold+ds+"_"+within+"_posthoc.txt", "w") as f:
                f.write(posthoc.to_string(header=True, index=False))
        else:
            with open(outfold+within+"_"+ds+"_posthoc.txt", "w") as f:
                f.write(posthoc.to_string(header=True, index=False))
    print()

    

    # plot the data
    ax = sns.pointplot(data=df, x=betw, y=within, hue=betw, dodge=True, capsize=.05, errorbar='se', order=orders, palette=sns.color_palette('bright'))
    # plt.ylim(3.5, 8)
    if ds == 'Trans_order':
        _ = plt.title('Transitive word order proportions'.format())
    else:
        _ = plt.title('N1 ratio and word order ({source})'.format(source=ds))
    # plt.style.use(plot_settings)
    # sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    if repl:
        if len(orders) > 3:
            plt.savefig(outfold+ds+"_"+within+".png")
        else:
            plt.savefig(outfold+within+"_"+ds+".png")
    plt.clf()
