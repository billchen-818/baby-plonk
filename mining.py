import pyethereum
u = pyethereum.utils
import time

#These are the operations that will end up in the tape
ops = [
    lambda x, y: x+y % 2**256,
    lambda x, y: x*y % 2**256,
    lambda x, y: x % y if y > 0 else x+y,
    lambda x, y: x & y,
    lambda x, y: x | y,
    lambda x, y: x ^ y
]


'''
the tape will be 'w' wide and 'd' operations deep
it is a list of triples [i, j, op], later used
in the tape's execution: xi = xi op xj 
'''
def gen_tape(seed, w, d):
    tape = []
    h = 0
    #Getting as much entropy out of a hash as possible
    for i in range(d):
        if h < 2**32:
            h = u.big_endian_to_int(u.sha3(seed+str(i)))
        v1 = h % w
        h /= w
        v2 = h % w
        h /= w
        op = ops[h % len(ops)]
        h /= len(ops)
        tape.append([v1, v2, op])
    return tape


def lshift(n):
    return 2**255 * (n % 2) + (n / 2)

#Generates the inputs to and evaluates the tape, the mining nonce can be taken to be in the seed
def gen_inputs(seed,w):
    #generating the tape's inputs
    v = []
    h = 0
    for i in range(w):
        if i % 1 == 0:
            h = u.big_endian_to_int(u.sha3(seed+str(i)))
        else:
            h = lshift(h)
        v.append(h)
    return v

#Evaluate tape on inputs (incorrect dimension of v is an unhandled exception)
def run_tape(v, tape):
    for t in tape:
        v[t[0]] = t[2](v[t[0]], v[t[1]])
    #Implemented in a blockchain, any additional hashes or timestamp would be added in the sha
    return str(v)
    
def sha_cap(s):
    return u.sha3(s)


def test(num_iterations, num_tape_evals, tape_w = 100, tape_d = 1000):
    time_generating_tape = 0.
    time_generating_inputs = 0.
    time_evaluating_tape = 0.
    time_sha_capping = 0.
    for i in range(num_iterations):
        t = time.time()
        tape = gen_tape(str(i), tape_w, tape_d)
        time_generating_tape += time.time() - t
        
        for i in xrange(num_tape_evals):
            t = time.time()
            v = gen_inputs(str(i), tape_w)
            time_generating_inputs += time.time() - t
            
            t = time.time()
            x = run_tape(v,tape)
            time_evaluating_tape += time.time() - t
            
            t = time.time()
            h = sha_cap(x)
            time_sha_capping += time.time() - t

    total_time = time_generating_tape + time_generating_inputs + time_evaluating_tape + time_sha_capping
    print "% of time generating tape:", time_generating_tape/total_time
    print "% of time generating inputs:", time_generating_inputs/total_time
    print "% of time evaluating tape:", time_evaluating_tape/total_time
    print "% of time sha-capping:", time_sha_capping/total_time
