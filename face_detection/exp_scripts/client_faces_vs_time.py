import argparse, socket, sys, select, cv2, os, pickle, time, Queue;
import numpy as np;
from threading import Thread;

"""

-	Create a queue with all the tasks
-	Create a thread for each service
-	The thread consumes tasks from
	the shared queue
-	Each thread itself is sequential
-	The service itself is probably
	I/O multiplexed

"""

class mysocket:
    '''demonstration class only
      - coded for clarity, not efficiency
    '''
    def __init__(self, sock=None, BUF_SIZE = 8192):
        self.BUF_SIZE = BUF_SIZE;
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        msg += "\END\n";
        MSGLEN = len(msg);
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myreceive(self):
        # print "Receiving Things..."
        chunks = []
        MSG_COMP = -1
        last_msg = '';
        while MSG_COMP < 0:
            chunk = self.sock.recv(self.BUF_SIZE);
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            last_msg = ''.join(chunks[-2:]);

            MSG_COMP = last_msg.find("\END", max(0, len(last_msg) - 
            	len(chunks[-1]) - 10))
            
        return ''.join([''.join(chunks[:-2]), last_msg[:MSG_COMP]])


def load_images():
    img_list = [];
    dirs = os.listdir(IMAGE_DIR);
    img_list = filter(lambda x: 'face-' in x, dirs);
    # img_list = map(lambda x: (x, os.path.getsize("%s/%s" % (IMAGE_DIR, x))), img_list);
    img_list = map(lambda x: (x, x.split('-')[1].split('.')[0].split('x')), img_list);
    img_list = map(lambda (x, y): (x, int(y[0]) * int(y[1])), img_list);
    img_list.sort(key = get_key);
    return img_list;

def worker_thread(input_queue, service_socket):
	while True:
		if can_run and not input_queue.empty():
			# print "Getting work done"
			# res = input_queue.get();
			# print len(res);
			# print len(res[0]);
			# print res
			# (i, task) = res;
			i, task = input_queue.get();
			start_time = time.time();
			mysocket(service_socket).mysend(pickle.dumps(task));
			response, process_time = pickle.loads(mysocket(service_socket).myreceive());
			# overall_time = time.time() - start_time;
			# prev_overall_time, prev_process_time = local_dict[i];
			# if prev_process_time < 0 and prev_overall_time < 0:
			# 	local_dict[i] = (overall_time, process_time);
			# else:
			# 	local_dict[i] = (overall_time + prev_overall_time, process_time + prev_process_time);
				# local_dict[i] = (time.time() - start_time, process_time);
			input_queue.task_done();
		
def main():
	parser = argparse.ArgumentParser();
	parser.add_argument("-p", "--port",
		help = "Port to serve on (Default is 50000)",
		type = int,
		default = 50000);

	args = parser.parse_args();
	
	server = Communicator(args.port, []);
	server.listen();
	# print args.port

def get_key(x):
    # _, i = x;
    # r, _ = i;
    # return r;
    return x[1];

def initLocalDict():
    kv_list = map(lambda x: (x, (-1, -1)), range(RUNS));
    return dict(kv_list);

def processResults(data):
    """
    Check validty of results first
    """
    for (overall, process) in data:
        if process > overall:
            print "Something not right, Overall is less than processing";
            print data
        if process < 0 or overall < 0:
            print "Something not right, time is less than 0";
            print data

    """
    Then find the average
    """
    overall, process = zip(*data);
    return map(lambda x: sum(x)/len(x), [overall, process]);


def splitFrame(frame, min_splits):
    splits = [frame];
    # print len(splits), len(splits[0]), len(splits[0][0]);
    while len(splits) < min_splits:
        h, w = splits[0].shape;
        if h > w:
            temp = map(lambda x: np.array_split(x, 2, 0), splits);
        else:
            temp = map(lambda x: np.array_split(x, 2, 1), splits);
        splits = [];
        map(lambda x: splits.extend(x), temp);
        # print splits[0].shape;
        # print len(splits)
    # for ar in splits:
    # 	print ar.shape
    return splits;

def generateTaskQueueSplits(task_list, service_list):
    input_queue = Queue.Queue();
    for (i, task) in enumerate(task_list):
        splits = splitFrame(task, len(service_list));
        tmp = map(lambda x: (x, splits), range(RUNS));
        tmp = map(lambda (x, sp): map(lambda y: (x, y), sp), tmp);
        tmp_final = [];
        map(lambda x: tmp_final.extend(x), tmp);
        # print len(tmp_final);
        # for l in tmp_final:
        # 	print len(l);
        # print len(tmp_final[0]);
        input_queue.put((i, tmp_final));
    return input_queue;
        


def generateTaskQueueCopies(task_list):
    input_queue = Queue.Queue();
    for (i, task) in enumerate(task_list):
        input_queue.put((i, map(lambda x: (x, task), range(RUNS))));
    return input_queue;

rpi1_ip = '172.20.64.55'
rpi2_ip = '172.20.64.110'

lt_feat_1 = ('localhost', 50000);
lt_feat_11 = ('localhost', 50004);
lt_feat_111 = ('localhost', 50005);
lt_feat_2 = ('localhost', 50001);
lt_feat_3 = ('localhost', 50002);

ed1_feat_1 = ('172.20.99.60', 50000);
ed1_feat_2 = ('172.20.99.60', 50001);
ed1_feat_3 = ('172.20.99.60', 50002);

ed2_feat_1 = ('172.20.96.110', 50000);
ed2_feat_2 = ('172.20.96.110', 50001);
ed2_feat_3 = ('172.20.96.110', 50002);

rpi1_feat_1 = (rpi1_ip, 50000);
rpi1_feat_2 = (rpi1_ip, 50001);
rpi1_feat_3 = (rpi1_ip, 50002);

rpi2_feat_1 = (rpi2_ip, 50000);
rpi2_feat_2 = (rpi2_ip, 50001);
rpi2_feat_3 = (rpi2_ip, 50002);

rpiKb_feat_1 = (rpi1_ip, 32503)
rpiKb_feat_2 = (rpi1_ip, 32745)
rpiKb_feat_3 = (rpi1_ip, 31425)

experiments = {
'exp1': ('faces-V-time_ED-1_feat-1.txt', [ed1_feat_1]),
'exp2': ('faces-V-time_ED-1_feat-2.txt', [ed1_feat_2]),
'exp3': ('faces-V-time_ED-1_feat-3.txt', [ed1_feat_3]),
'exp4': ('faces-V-time_ED-2_feat-1.txt', [ed1_feat_1, ed2_feat_1]),
'exp5': ('faces-V-time_ED-2_feat-2.txt', [ed1_feat_2, ed2_feat_2]),
'exp6': ('faces-V-time_ED-2_feat-3.txt', [ed1_feat_3, ed2_feat_3]),
'exp7': ('faces-V-time_PI-1_feat-1.txt', [rpi1_feat_1]),
'exp8': ('faces-V-time_PI-1_feat-2.txt', [rpi1_feat_2]),
'exp9': ('faces-V-time_PI-1_feat-3.txt', [rpi1_feat_3]),
'exp10': ('faces-V-time_PI-2_feat-1.txt', [rpi1_feat_1, rpi2_feat_1]),
'exp11': ('faces-V-time_PI-2_feat-2.txt', [rpi1_feat_2, rpi2_feat_2]),
'exp12': ('faces-V-time_PI-2_feat-3.txt', [rpi1_feat_3, rpi2_feat_3]),
'exp0': ('faces-V-time_LT-1_feat-1.txt', [lt_feat_1]),
'exp13': ('faces-V-time_LT-1_feat-2.txt', [lt_feat_2]),
'exp14': ('faces-V-time_LT-1_feat-3.txt', [lt_feat_3]),
'exp15': ('faces-V-time_PI-2_ED-2_feat-1.txt', [rpi1_feat_1, rpi2_feat_1, ed1_feat_1, ed2_feat_1]),
'exp16': ('faces-V-time_PI-2_ED-2_feat-2.txt', [rpi1_feat_2, rpi2_feat_2, ed1_feat_2, ed2_feat_2]),
'exp17': ('faces-V-time_PI-2_ED-2_feat-3.txt', [rpi1_feat_3, rpi2_feat_3, ed1_feat_3, ed2_feat_3]),
'exp001' : ('test_output.txt', [lt_feat_1]),
'exp002' : ('test_output.txt', [lt_feat_1, lt_feat_11]),
'exp003' : ('test_output.txt', [lt_feat_1, lt_feat_11, lt_feat_111]),
'exp004' : ('test_output.txt', [rpi1_feat_1]),
'exp20': ('faces-V-time_PIDocker-1_feat-1.txt', [rpi1_feat_1]),
'exp21': ('faces-V-time_PIDocker-1_feat-2.txt', [rpi1_feat_2]),
'exp22': ('faces-V-time_PIDocker-1_feat-3.txt', [rpi1_feat_3]),
'exp23': ('faces-V-time_PIDocker-2_feat-1.txt', [rpi1_feat_1, rpi2_feat_1]),
'exp24': ('faces-V-time_PIDocker-2_feat-2.txt', [rpi1_feat_2, rpi2_feat_2]),
'exp25': ('faces-V-time_PIDocker-2_feat-3.txt', [rpi1_feat_3, rpi2_feat_3]),
'exp26': ('faces-V-time_PIKube-2_feat-1.txt', [rpiKb_feat_1]),
'exp27': ('faces-V-time_PIKube-2_feat-2.txt', [rpiKb_feat_2]),
'exp28': ('faces-V-time_PIKube-2_feat-3.txt', [rpiKb_feat_3]),
}
"""
Experiment Configuration
"""
IMAGE_DIR = "../../../face_examples/faces/";
OUPUT_DIR = "../raw_data/";
EXP, service_list = experiments[sys.argv[1]];
RUNS = 1;




"""
Initialization of the experiment
"""
outfile = "%s%s" % (OUPUT_DIR, EXP);
results = {};
# service_list = [('localhost', 50000), ('localhost', 50001)];
# service_list = [('172.20.99.60', 50000)];



"""
Actual Experiment
"""

init_img_list = load_images();
img_list = map(lambda (f, res): (cv2.imread("%s%s" % (IMAGE_DIR, f)), res), init_img_list);
img_list = map(lambda (f, res): (cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), res), img_list);
img_list = map(lambda (f, res): f, img_list);
# for i in img_list:
# 	print i.shape;
# sys.exit()

# input_queue = generateTaskQueueSplits(img_list, service_list);
input_queue = generateTaskQueueSplits(img_list, service_list);


service_list = map(lambda x: (socket.socket(socket.AF_INET, socket.SOCK_STREAM), x), service_list);
map(lambda (x, y): x.connect(y), service_list);
service_socket_list = map(lambda (x, _): x, service_list);

# map(lambda x: input_queue.put(x), enumerate(img_list));

local_dict = None;
task_queue = Queue.Queue();
can_run = False;

worker_threads = map(lambda s: Thread(target = worker_thread, args = (task_queue, s, )), service_socket_list);
map(lambda x: x.setDaemon(True), worker_threads);
map(lambda x: x.start(), worker_threads);

while not input_queue.empty():
    (i, task_list) = input_queue.get();
    map(lambda x: task_queue.put(x), task_list);
    local_dict = initLocalDict();
    overall_time = time.time();
    can_run = True;
    task_queue.join();
    overall_time = time.time() - overall_time;
    can_run = False;
    # results[i] = processResults(local_dict.values());
    results[i] = (overall_time, overall_time/RUNS)

# sys.exit()

final = enumerate(map(lambda (_, s): s, init_img_list));
final = map(lambda (i, size): (size, (results[i][0], results[i][1])), final);
# print final

with open(outfile, 'w') as f:
    for (s, (o, p)) in final:
        f.write("%s\t%s\t%s\n" % (s, o , p))
# print input_queue.qsize();
# while not input_queue.empty():
#     print input_queue.get()

# print len(input_queue.get()[1]);

# input_queue.join();

# print results

# print load_images()