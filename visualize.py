# CSCE 312-200

# supplemental project for honours credit - HDL file visualiser
# works on chips with only primitive gates (can extend functionality to Mux/DMux/Black box with more time)
# instructions: edit filename with name of HDL file (in same working direc) and execute THIS script


from nand2tetris_hdl_parser import parse_hdl
import re
from topsort import Chip_Graph, Chip_Graph_BFS
from schemdraw import logic
from schemdraw import elements
from schemdraw import Drawing
from schemdraw.parsing import logicparse
from schemdraw.elements import ElementDrawing

'''GLOBALS'''
id2part = {}
op2expr = {}

infile = open("Palindrome.hdl","r").read()
hdl = parse_hdl(infile) # cheers Teddy Heinen !

chip_keys = [key for key in hdl.keys()]
ins = [p['name'] for p in hdl['inputs']]
outs = [p['name'] for p in hdl['outputs']]
chip_parts = hdl[chip_keys[3]]

def V(parts):
    '''
        this function returns a list of vertices comprising all the parts in the chip
            - the parts are represented by their ids (1..n) which are guarunteed unique
            - as well as their boolstrenated pin names
            - it also populates the id2part dictionary with the numerical ids as keys and the parts as values
            *** this function is automatically called by E, there is no need to call it ***
            - it also populates the op2expr dictionary with the boolean expression corresponding to the part's output,
            surrounded by parentheses
    '''

    V = []
    pc = 0

    for p in parts:
        if str(p['name']) != 'Not':
            boolstr = '('
            boolstr += str(p['external'][0]['name']).strip()
            boolstr += ' '
            boolstr += str(p['name']).lower().strip()
            boolstr += ' '
            boolstr += str(p['external'][1]['name']).strip()
            boolstr += ')'

            p['boolstr'] = tuple([str(p['external'][2]['name']), boolstr])
            op2expr[str(p['external'][2]['name'])] = boolstr
        else:
            boolstr = '(not '
            boolstr += str(p['external'][0]['name']).strip()
            boolstr += ')'

            p['boolstr'] = tuple([str(p['external'][1]['name']), boolstr])
            op2expr[str(p['external'][1]['name'])] = boolstr

        p['id'] = pc

        V.append(pc)
        id2part[pc] = p

        pc += 1

    return V
def E():
    '''
    this function returns a list of tuples representing the edges found in the graph
        - it may not include every vertex in it, only vertices which have an outgoing edge
    '''

    edges = []
    parts = [id2part[p] for p in V(chip_parts)]

    for p in parts:

        o = indexOfOut(p)
        pc = 0

        outputs = []
        for pin in p['external']:
            if pc >= o:
                outputs.append(pin['name'])
            pc += 1

        for pp in parts:
            if pp['id'] == p['id']:
                continue

            o = indexOfOut(pp)
            ppc = 0

            inputs = []
            for pin in pp['external']:
                if ppc < o:
                    inputs.append(pin['name'])
                ppc += 1

            for a in outputs:
                for b in inputs:
                    if a == b:
                        e = [p['id'], pp['id']]
                        if tuple(e) not in edges:
                            edges.append(tuple(e))

    return edges
def indexOfOut(part):
    '''
    helper function to distinguish between external input and output pins
        *** an edge must be directed from one part's output to another part's input ***
    '''

    idx = 0
    pins = part['internal']
    for d in pins:
        if d['name'] != 'out':
            idx += 1

    return idx
def logician(outs, ins):
    '''this function recursively builds the logic tree/expression starting from
    each output of the chip and working it's way down to the inputs. we will pass it
    directly to elements4output in order for the drawing to render'''

    feed = []

    def reeval(pin):
        if pin not in op2expr.keys():
            return str(pin)

        subterms = re.sub(r'[()]', '', op2expr[pin]).split(' ')
        inputPinsInExpr = [n for n in subterms if n in ins]

        if not any(inputPinsInExpr):
            if len(subterms) == 3:
                subterms[0] = reeval(subterms[0])
                subterms[2] = reeval(subterms[2])
                return (str(subterms[0]) + str(' ') + str(subterms[1]) + str(' ') + str(subterms[2]))
            elif len(subterms) == 2:
                subterms[1] = reeval(subterms[1])
                return (str(subterms[0]) + str(' ') + str(subterms[1]))

        elif len(inputPinsInExpr) == 1:
            if len(subterms) == 3:
                if inputPinsInExpr[0] == subterms[0]:
                    subterms[2] = reeval(subterms[2])
                    return (str('(') + str(subterms[0]) + str(' ') + str(subterms[1]) + str(' ') + str(subterms[2]) + str(')'))
                else:
                    subterms[0] = reeval(subterms[0])
                    return (str('(') + str(subterms[0]) + str(' ') + str(subterms[1]) + str(' ') + str(subterms[2]) + str(')'))

            elif len(subterms) == 2:
                return (str('(') + str(subterms[0]) + str(' ') + str(subterms[1]) + str(')'))

        else: # 2 input pins, expression must have 3 terms
            return (str('(') + str(subterms[0]) + str(' ') + str(subterms[1]) + str(' ') + str(subterms[2]) + str(')'))

    for op in outs:
        expr = ''

        terms = re.sub(r'[()]', '', op2expr[op]).split(' ')

        if len(terms) == 3:
            expr += str(reeval(terms[0]))
            expr += (str(' ') + str(terms[1]) + str(' '))
            expr += str(reeval(terms[2]))
        else:
            expr += str(terms[0])
            expr += str(reeval(terms[1]))

        feed.append(tuple([op, expr]))

    return feed
def elements4output(output2eq, cols=3, dx=5, dy=2):
    ''' outputs drawing from list of outputs and associated logic equations (strings) '''

    d = Drawing(fontsize=12)
    for i, e in enumerate(output2eq):
        y = i//cols*-dy
        x = (i%cols) * dx

        d += ElementDrawing(logicparse(e[1], outlabel=e[0], gateH=1.25*len(output2eq)), show=False, d='right', xy=[x,y])

    return d.draw()

g = Chip_Graph_BFS(len(V(chip_parts)))
for tpl in E():
    g.add_edge(tpl[0], tpl[1])

elements4output(logician(outs, ins))
