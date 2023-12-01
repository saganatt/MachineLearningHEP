#############################################################################
##  © Copyright CERN 2018. All rights not expressly granted are reserved.  ##
##                 Author: Gian.Michele.Innocenti@cern.ch                  ##
## This program is free software: you can redistribute it and/or modify it ##
##  under the terms of the GNU General Public License as published by the  ##
## Free Software Foundation, either version 3 of the License, or (at your  ##
## option) any later version. This program is distributed in the hope that ##
##  it will be useful, but WITHOUT ANY WARRANTY; without even the implied  ##
##     warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    ##
##           See the GNU General Public License for more details.          ##
##    You should have received a copy of the GNU General Public License    ##
##   along with this program. if not, see <https://www.gnu.org/licenses/>. ##
#############################################################################

"""
Methods to: model performance evaluation
"""
import itertools
from io import BytesIO
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn
from sklearn.model_selection import cross_val_score, cross_val_predict, train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_curve, roc_auc_score, auc, confusion_matrix, precision_recall_curve
from sklearn.metrics import mean_squared_error

HIST_COLORS = ['r', 'b', 'g']

def cross_validation_mse(names_, classifiers_, x_train, y_train, cv_, ncores):
    df_scores = pd.DataFrame()
    for name, clf in zip(names_, classifiers_):
        if "Keras" in name:
            ncores = 1
        kfold = StratifiedKFold(n_splits=cv_, shuffle=True, random_state=1)
        scores = cross_val_score(clf, x_train, y_train, cv=kfold,
                                 scoring="neg_mean_squared_error", n_jobs=ncores)
        tree_rmse_scores = np.sqrt(-scores)
        df_scores[name] = tree_rmse_scores
    return df_scores


def cross_validation_mse_continuous(names_, classifiers_, x_train, y_train, cv_, ncores):
    df_scores = pd.DataFrame()
    for name, clf in zip(names_, classifiers_):
        if "Keras" in name:
            ncores = 1
        scores = cross_val_score(clf, x_train, y_train, cv=cv_,
                                 scoring="neg_mean_squared_error", n_jobs=ncores)
        tree_rmse_scores = np.sqrt(-scores)
        df_scores[name] = tree_rmse_scores
    return df_scores


def plot_cross_validation_mse(names_, df_scores_, suffix_, folder):
    figure1 = plt.figure(figsize=(20, 15))
    i = 1
    for name in names_:
        ax = plt.subplot(2, (len(names_)+1)/2, i)
        ax.set_xlim([0, (df_scores_[name].mean()*2)])
        plt.hist(df_scores_[name].values, color="blue")
        mystring = '$\\mu=%8.2f, \\sigma=%8.2f$' % (df_scores_[name].mean(), df_scores_[name].std())
        plt.text(0.2, 4., mystring, fontsize=16)
        plt.title(name, fontsize=16)
        plt.xlabel("scores RMSE", fontsize=16)
        plt.ylim(0, 5)
        plt.ylabel("Entries", fontsize=16)
        figure1.subplots_adjust(hspace=.5)
        i += 1
    plotname = folder+'/scoresRME%s.png' % (suffix_)
    plt.savefig(plotname)
    img_scoresRME = BytesIO()
    plt.savefig(img_scoresRME, format='png')
    img_scoresRME.seek(0)
    return img_scoresRME


def plotdistributiontarget(names_, testset, myvariablesy, suffix_, folder):
    figure1 = plt.figure(figsize=(20, 15))
    i = 1
    for name in names_:
        _ = plt.subplot(2, (len(names_)+1)/2, i)
        plt.hist(testset[myvariablesy].values, color="blue", bins=100, label="true value")
        plt.hist(
            testset['y_test_prediction'+name].values,
            color="red", bins=100, label="predicted value")
        plt.title(name, fontsize=16)
        plt.xlabel(myvariablesy, fontsize=16)
        plt.ylabel("Entries", fontsize=16)
        figure1.subplots_adjust(hspace=.5)
        i += 1
    plt.legend(loc="center right")
    plotname = folder+'/distributionregression%s.png' % (suffix_)
    plt.savefig(plotname)
    img_dist_reg = BytesIO()
    plt.savefig(img_dist_reg, format='png')
    img_dist_reg.seek(0)
    return img_dist_reg


def plotscattertarget(names_, testset, myvariablesy, suffix_, folder):
    _ = plt.figure(figsize=(20, 15))
    i = 1
    for name in names_:
        figure1 = plt.subplot(2, (len(names_)+1)/2, i)
        plt.scatter(
            testset[myvariablesy].values,
            testset['y_test_prediction'+name].values, color="blue")
        plt.title(name, fontsize=16)
        plt.xlabel(myvariablesy + "true", fontsize=20)
        plt.ylabel(myvariablesy + "predicted", fontsize=20)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        figure1.subplots_adjust(hspace=.5)
        i += 1
    plotname = folder+'/scatterplotregression%s.png' % (suffix_)
    plt.savefig(plotname)
    img_scatt_reg = BytesIO()
    plt.savefig(img_scatt_reg, format='png')
    img_scatt_reg.seek(0)
    return img_scatt_reg


def confusion(names_, classifiers_, suffix_, x_train, y_train, cvgen, folder):
    figure1 = plt.figure(figsize=(25, 15))  # pylint: disable=unused-variable
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.4, hspace=0.2)

    i = 1
    for name, clf in zip(names_, classifiers_):
        ax = plt.subplot(2, (len(names_)+1)/2, i)
        y_train_pred = cross_val_predict(clf, x_train, y_train, cv=cvgen)
        conf_mx = confusion_matrix(y_train, y_train_pred)
        row_sums = conf_mx.sum(axis=1, keepdims=True)
        norm_conf_mx = conf_mx / row_sums
        np.fill_diagonal(norm_conf_mx, 0)
        df_cm = pd.DataFrame(norm_conf_mx, range(2), range(2))
        sn.set(font_scale=1.4)  # for label size
        ax.set_title(name+"tot diag=0")
        sn.heatmap(df_cm, annot=True, annot_kws={"size": 16})  # font size
        ax.set_xlabel('Predicted labels')
        ax.set_ylabel('True labels')
        ax.xaxis.set_ticklabels(['signal', 'background'])
        ax.yaxis.set_ticklabels(['signal', 'background'])

        i += 1
    plotname = folder+'/confusion_matrix%s_Diag0.png' % (suffix_)
    plt.savefig(plotname)
    img_confmatrix_dg0 = BytesIO()
    plt.savefig(img_confmatrix_dg0, format='png')
    img_confmatrix_dg0.seek(0)

    figure2 = plt.figure(figsize=(20, 15))  # pylint: disable=unused-variable
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.4, hspace=0.2)

    i = 1
    for name, clf in zip(names_, classifiers_):
        ax = plt.subplot(2, (len(names_)+1)/2, i)
        y_train_pred = cross_val_predict(clf, x_train, y_train, cv=cvgen)
        conf_mx = confusion_matrix(y_train, y_train_pred)
        row_sums = conf_mx.sum(axis=1, keepdims=True)
        norm_conf_mx = conf_mx / row_sums
        df_cm = pd.DataFrame(norm_conf_mx, range(2), range(2))
        sn.set(font_scale=1.4)  # for label size
        ax.set_title(name)
        sn.heatmap(df_cm, annot=True, annot_kws={"size": 16})  # font size
        ax.set_xlabel('Predicted labels')
        ax.set_ylabel('True labels')
        ax.xaxis.set_ticklabels(['signal', 'background'])
        ax.yaxis.set_ticklabels(['signal', 'background'])

        i += 1
    plotname = folder+'/confusion_matrix%s.png' % (suffix_)
    plt.savefig(plotname)
    img_confmatrix = BytesIO()
    plt.savefig(img_confmatrix, format='png')
    img_confmatrix.seek(0)
    return img_confmatrix_dg0, img_confmatrix


def plot_precision_recall(names_, classifiers_, suffix_, x_train, y_train,
                          nkfolds, folder, multiclass_labels):
    if len(names_) == 1:
        figure1 = plt.figure(figsize=(20, 15))  # pylint: disable=unused-variable
    else:
        figure1 = plt.figure(figsize=(25, 15))  # pylint: disable=unused-variable
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.4, hspace=0.2)

    for ind, (name, clf) in enumerate(zip(names_, classifiers_)):
        y_proba = cross_val_predict(clf, x_train, y_train, cv=nkfolds, method="predict_proba")
        if len(names_) > 1:
            plt.subplot(2, (len(names_)+1)/2, ind)
        for cls_hyp, (label_hyp, color) in enumerate(zip(multiclass_labels, HIST_COLORS)):
            y_scores = y_proba[:, cls_hyp]
            print(f"y proba:\n{y_proba}\nscores for class {label_hyp}:\n{y_scores}")
            precisions, recalls, thresholds = precision_recall_curve(y_train == cls_hyp, y_scores)
            print(f"precisions:\n{precisions}\nrecalls\n{recalls}")
            plt.plot(thresholds, precisions[:-1], f"{color}--",
                     label=f"Precision {label_hyp} = TP/(TP+FP)", linewidth=5.0)
            plt.plot(thresholds, recalls[:-1], f"{color}-", alpha=0.5,
                     label=f"Recall {label_hyp} = TP/(TP+FN)", linewidth=5.0)
        plt.xlabel('Probability', fontsize=20)
        plt.ylabel('Precision or Recall', fontsize=20)
        plt.title('Precision, Recall '+name, fontsize=20)
        plt.legend(loc="best", prop={'size': 30})
        plt.ylim([0, 1])
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
    plt.savefig(f"{folder}/precision_recall{suffix_}.png")


def plot_roc(names_, classifiers_, suffix_, x_train, y_train, nkfolds, folder,
             multiclass_labels):
    figure = plt.figure(figsize=(20, 15))  # pylint: disable=unused-variable
    for name, clf in zip(names_, classifiers_):
        y_proba = cross_val_predict(clf, x_train, y_train, cv=nkfolds, method="predict_proba")
        for cls_hyp, (label_hyp, color) in enumerate(zip(multiclass_labels, HIST_COLORS)):
            fpr, tpr, _ = roc_curve(y_train == cls_hyp, y_proba[:, cls_hyp])
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, f"{color}-", label=f"ROC {name} {label_hyp} vs rest, "\
                     f"AUC = {roc_auc:.2f}", linewidth=5.0)
    plt.xlabel('False Positive Rate or (1 - Specifity)', fontsize=20)
    plt.ylabel('True Positive Rate or Sensitivity', fontsize=20)
    plt.title('Receiver Operating Characteristic', fontsize=20)
    plt.legend(loc="lower center", prop={'size': 30})
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.savefig(f"{folder}/ROCcurve{suffix_}.png")


def plot_two_class_efficiences(names_, classifiers_, suffix_, x, y, folder,
                               multiclass_labels):
    for name, clf in zip(names_, classifiers_):
        # Not using cross_val as we do not compare different classifiers
        y_scores = clf.predict_proba(x)
        #scores_sum = y_scores.sum(axis=1)
        #non_ones = scores_sum[scores_sum != 1.0]
        #print(f"sum of scores:\n{scores_sum}\nnot one:\n{non_ones}")
        figure = plt.figure(figsize=(20, 15)) #pylint: disable=unused-variable
        label_pairs = itertools.combinations(multiclass_labels, 2)
        for label_pair, color in zip(label_pairs, HIST_COLORS):
            ind_lab1 = multiclass_labels.index(label_pair[0])
            ind_lab2 = multiclass_labels.index(label_pair[1])
            mask_or = np.logical_or(y == ind_lab1, y == ind_lab2)
            for ind, (ind_lab, alpha) in enumerate(zip((ind_lab1, ind_lab2), (1.0, 0.5))):
                mask = y == ind_lab
                fpr, tpr, _ = roc_curve(mask[mask_or], y_scores[mask_or, ind_lab])
                roc_auc = auc(fpr, tpr)
                #roc_auc_2 = roc_auc_score(y, y_scores, multi_class="ovo")
                #print(f"ROC by fpr, tpr: {roc_auc} roc from fun: {roc_auc_2}")
                plt.plot(fpr, tpr, f"{color}-", alpha=alpha, label=f"ROC "\
                         f"{label_pair[ind]} vs {label_pair[1-ind]} (AUC = {roc_auc:.2f})",
                         linewidth=5.0)
        plt.xlabel('First class efficiency', fontsize=20)
        plt.ylabel('Second class efficiency', fontsize=20)
        plt.title('Receiver Operating Characteristic', fontsize=20)
        plt.legend(loc="lower center", prop={'size': 30})
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        plt.savefig(f"{folder}/Effcurve{name}{suffix_}.png")


def plot_learning_curves(names_, classifiers_, suffix_, folder, x_data, y_data, npoints):
    figure1 = plt.figure(figsize=(20, 15))
    i = 1
    x_train, x_val, y_train, y_val = train_test_split(x_data, y_data, test_size=0.2)
    for name, clf in zip(names_, classifiers_):
        if len(names_) > 1:
            plt.subplot(2, (len(names_)+1)/2, i)
        train_errors, val_errors = [], []
        high = len(x_train)
        low = 100
        step_ = int((high-low)/npoints)
        arrayvalues = np.arange(start=low, stop=high, step=step_)
        for m in arrayvalues:
            clf.fit(x_train[:m], y_train[:m])
            y_train_predict = clf.predict(x_train[:m])
            y_val_predict = clf.predict(x_val)
            train_errors.append(mean_squared_error(y_train_predict, y_train[:m]))
            val_errors.append(mean_squared_error(y_val_predict, y_val))
        plt.plot(arrayvalues, np.sqrt(train_errors), "r-+", linewidth=5, label="training")
        plt.plot(arrayvalues, np.sqrt(val_errors), "b-", linewidth=5, label="testing")
        plt.ylim([0, np.amax(np.sqrt(val_errors))*2])
        plt.title("Learning curve "+name, fontsize=20)
        plt.xlabel("Training set size", fontsize=20)
        plt.ylabel("RMSE", fontsize=20)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        if len(names_) > 1:
            figure1.subplots_adjust(hspace=.5)
        plt.legend(loc="best", prop={'size': 30})
        i += 1
    plt.savefig(f"{folder}/learning_curve{suffix_}.png")


def plot_overtraining(names, classifiers, suffix, x_train, y_train, x_val, y_val, y_train_onehot, y_val_onehot, folder,
                      multiclass_labels, bins=50):
    for name, clf in zip(names, classifiers):
        predict_probs_train = clf.predict_proba(x_train)
        predict_probs_test = clf.predict_proba(x_val)
        for cls_hyp, label_hyp in enumerate(multiclass_labels):
            fig = plt.figure(figsize=(10, 8))
            for cls, (label, color) in enumerate(zip(multiclass_labels, HIST_COLORS)):
                cond1 = y_train == cls
                cond_one_hot = y_train_onehot.iloc[:, cls]
                print(f"Train disagreement: {cond1[np.logical_xor(cond1, cond_one_hot)]}")
                plt.hist(predict_probs_train[y_train == cls, cls_hyp],
                         color=color, alpha=0.5, range=[0, 1], bins=bins,
                         histtype='stepfilled', density=True, label=f'{label}, train')
                predicted_probs = predict_probs_test[y_val == cls, cls_hyp]
                hist, bins = np.histogram(predicted_probs, bins=bins, range=[0, 1], density=True)
                scale = len(predicted_probs) / sum(hist)
                err = np.sqrt(hist * scale) / scale
                center = (bins[:-1] + bins[1:]) / 2
                plt.errorbar(center, hist, yerr=err, fmt='o', c=color, label=f'{label}, test')
            plt.xlabel(f"ML score for {label_hyp}", fontsize=15)
            plt.ylabel("Arbitrary units", fontsize=15)
            plt.legend(loc="best", frameon=False, fontsize=15)
            plt.yscale("log")
            fig.savefig(f"{folder}/ModelOutDistr_{label_hyp}_{name}_{suffix}.png")


def roc_train_test(names_, classifiers_, suffix_, x_train, y_train, x_test, y_test,
                   folder, multiclass_labels, binmin, binmax):
    fig = plt.figure(figsize=(20, 15))
    for name, clf in zip(names_, classifiers_):
        for (x, y), set_name in zip(((x_train, y_train), (x_test, y_test)), ("train", "test")):
            y_pred = clf.predict_proba(x)
            print(f"y pred:\n{y_pred}\ny:\n{y}")
            for cls_hyp, (label_hyp, color, ls, alpha) in \
                    enumerate(zip(multiclass_labels, HIST_COLORS, ("-", "-."), (0.4, 0.8))):
                print(f"y for {cls_hyp}:\n{y.iloc[:, cls_hyp]}\ny pred for {cls_hyp}:\n{y_pred[:, cls_hyp]}")
                fpr, tpr, _ = roc_curve(y.iloc[:, cls_hyp], y_pred[:, cls_hyp])
                roc_auc = auc(fpr, tpr)
                plt.plot(fpr, tpr, f"{color}{ls}", lw=3, alpha=alpha,
                         label=f"ROC {name} {label_hyp} vs rest, {set_name} set, "\
                               f"AUC = {roc_auc:.4f}")

    plt.text(0.7, 0.5,
             f" ${binmin} < p_\\mathrm{{T}}/(\\mathrm{{GeV}}/c) < {binmax}$",
             verticalalignment="center", transform=fig.gca().transAxes, fontsize=30)

    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate', fontsize=30)
    plt.ylabel('True Positive Rate', fontsize=30)
    plt.legend(loc='lower right', prop={'size': 25})
    plt.tick_params(labelsize=20)
    plot_name = f'{folder}/ROCtraintest{suffix_}.png'
    fig.savefig(plot_name)
    # FIXME: Why are some plots saved in pickle?
    plot_name = plot_name.replace('png', 'pickle')
    with open(plot_name, 'wb') as out:
        pickle.dump(fig, out)
    plt.close(fig)
