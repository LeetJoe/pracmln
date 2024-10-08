
import json


letter_dict = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

domain = ['entity']


def num2letter(num):
    num = int(num)
    result = ''
    while True:
        div = num // 26
        mod = num % 26
        result = letter_dict[mod] + result
        num = div
        if div == 0:
            break

    return result


def load(file, pred_num):
    fi = open(file, 'r')
    preds = []
    evids = []
    for line in fi:
        line = line.strip()
        linelist = line.split('\t')
        sub = 'Ent_' + num2letter(linelist[0])
        pred = 'pred_' + num2letter(linelist[1])
        obj = 'Ent_' + num2letter(linelist[2])

        pred_inv = 'pred_' + num2letter(int(linelist[1]) + int(pred_num))

        if pred not in preds:
            preds.append(pred)
            preds.append(pred_inv)

        evids.append(pred + '(' + sub + ', ' + obj + ')')
        evids.append(pred_inv + '(' + obj + ', ' + sub + ')')

    fi.close()
    return preds, evids


def load_rules(file):
    tlogc_rules = json.load(open(file, 'r'))

    formulas = []
    for hr in tlogc_rules:
        for rule in tlogc_rules[hr]:
            formula_str = rule2formula(rule)
            formulas.append([rule['conf'], formula_str])

    return formulas


def load_learnt_rules(file):
    weighted_rules = json.load(open(file, 'r'))
    formulas = []
    for rule in weighted_rules:
        formula_str = rule2formula(rule)
        formulas.append([rule['conf'], formula_str])

    return formulas


def rule2formula(rule):
    i = 0
    formula = ''
    sub0 = ''
    obj0 = ''
    for rel in rule['body_rels']:
        pred = 'pred_' + num2letter(rel)
        sub = 'var_' + letter_dict[i]
        i += 1
        obj = 'var_' + letter_dict[i]
        if formula != '':
            formula += '^'
        else:
            sub0 = sub
        formula += pred + '(' + sub + ', ' + obj + ')'
        obj0 = obj

    pred = 'pred_' + num2letter(rule['head_rel'])
    formula += '=>' + pred + '(' + sub0 + ', ' + obj0 + ')'
    return formula


predicates, train = load('icews14/origin/train.del', 230)

preds, test = load('icews14/origin/test.del', 230)

for pred in preds:
    if pred not in predicates:
        predicates.append(pred)

for i in range(len(predicates)):
    predicates[i] = predicates[i] + '(entity, entity)'

# mln with unlearnt weight
formulas = load_rules('icews14/origin/tlogic_rules.json')

fo = open('icews14/mlns/icews14.mln', 'w')
fo.write('//Predicates\n')
for pred in predicates:
    fo.write(pred + '\n')
fo.write('\n//Formulas\n')
for formula in formulas:
    fo.write(str(formula[0]) + ' ' + formula[1] + '\n')

fo.close()

# mln with learnt weight from MLN from tLogicNet
formulas = load_learnt_rules('icews14/rule.txt_0.85_1000_0.03_f2.formula')

fo = open('icews14/mlns/learnt.tlogicnet.train.icews14.mln', 'w')
fo.write('//Predicates\n')
for pred in predicates:
    fo.write(pred + '\n')
fo.write('\n//Formulas\n')
for formula in formulas:
    fo.write(str(formula[0]) + ' ' + formula[1] + '\n')

fo.close()

# train data
fo = open('icews14/dbs/icews14_train.db', 'w')
for evid in train:
    fo.write(evid + '\n')

fo.close()

# test data
fo = open('icews14/dbs/icews14_test.db', 'w')
for evid in test:
    fo.write(evid + '\n')

fo.close()



