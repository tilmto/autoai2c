from random import random, randint,shuffle
import numpy as np
import test_for_eyeriss as simnas
import time
from itertools import combinations,permutations
import copy
from  multiprocessing import Queue
import multiprocessing
import math
from ev_util import *
#the code assume that the life evaluation process takes much longer time than sorting process
#the code then is optimized towards such direction 


        
class ev_dict():
    def __init__(self,stride_list,net_arch,df_order,prop_m=0.5,max_pop=600,dying_rate=0.2,true_df_order=None,hw_spec=default_hw):
        self.prop_m=prop_m                                                              #mutation probability
        self.max_pop=max_pop
        self.dying_rate=dying_rate=0.2                                                          #the dying_rate is also aimed to allowing only elites to have children
        self.stride_list=stride_list
        self.net_arch=net_arch
        self.df_order=df_order
        self.true_df_order=true_df_order
        self.best_score=None
        self.hw_spec=hw_spec
        ###################################################
        #if u dont want to fix noc for the entire design
        #remove the following special handling cases and comment out all merge_noc
        ###################################################

        # #special handling for noc
        # noc=sample_noc(net_arch,df_order)
        # #currently best noc 
        # #rs
        # #noc={'ch_out': 32, 'ch_in': 3, 'col_out': 1}
        # #os
        # #noc={'ch_out': 1, 'col_out': 1, 'row_out': 1}
        # #ws
        # #noc={'ch_out': 8, 'ch_in': 1}
        # #modify net_arch
        # (net_arch,noc)=modify_param_for_noc(net_arch,noc)
        # print(noc)
        # #print(net_arch[0])
        
        #generate factor list according to a certain config_dict
        self.arch_factor_list=arch_factor_list_dict(self.net_arch)
        
        #test basic ev features
        #self.test()
        
    def test(self):
        #evolution util function testing space
        str1=arch_random_pop(self.net_arch,self.df_order,self.arch_factor_list)
        str2=arch_random_pop(self.net_arch,self.df_order,self.arch_factor_list)
        #print(str1)
        #print(str2)
        str3=arch_give_birth(str1,str2,net_arch)
        str4=arch_mutate(str3,1,self.arch_factor_list)
        # print(str4)  

        #reference design from pengfei's experiments RS 
        test_arch=[{'ch_out_rf': 16, 'ch_out_noc': 2, 'ch_out_gb': 2, 'ch_out_dram': 1, 'ch_in_rf': 1, 'ch_in_noc': 1, 'ch_in_gb': 3, 'batch_rf': 1, 'batch_dram': 1, 'col_out_noc': 7, 'col_out_dram': 8, 'row_out_rf': 56, 'row_kernel_rf': 11, 'col_kernel_noc': 11},\
         {'ch_out_rf': 16, 'ch_out_noc': 2, 'ch_out_gb': 2, 'ch_out_dram': 4, 'ch_in_rf': 2, 'ch_in_noc': 1, 'ch_in_gb': 24, 'batch_rf': 1, 'batch_dram': 1, 'col_out_noc': 27, 'col_out_dram': 1, 'row_out_rf': 27, 'row_kernel_rf': 5, 'col_kernel_noc': 5},\
         {'ch_out_rf': 16, 'ch_out_noc': 4, 'ch_out_gb': 4, 'ch_out_dram': 6, 'ch_in_rf': 4, 'ch_in_noc': 1, 'ch_in_gb': 64, 'batch_rf': 1, 'batch_dram': 1, 'col_out_noc': 13, 'col_out_dram': 1, 'row_out_rf': 13, 'row_kernel_rf': 3, 'col_kernel_noc': 3},\
         {'ch_out_rf': 16, 'ch_out_noc': 2, 'ch_out_gb': 2, 'ch_out_dram': 6, 'ch_in_rf': 3, 'ch_in_noc': 2, 'ch_in_gb': 32, 'batch_rf': 1, 'batch_dram': 1, 'col_out_noc': 13, 'col_out_dram': 1, 'row_out_rf': 13, 'row_kernel_rf': 3, 'col_kernel_noc': 3}, \
         {'ch_out_rf': 16, 'ch_out_noc': 2, 'ch_out_gb': 2, 'ch_out_dram': 4, 'ch_in_rf': 3, 'ch_in_noc': 2, 'ch_in_gb': 32, 'batch_rf': 1, 'batch_dram': 1, 'col_out_noc': 13, 'col_out_dram': 1, 'row_out_rf': 13, 'row_kernel_rf': 3, 'col_kernel_noc': 3}]

        print(arch_life(test_arch,self.stride_list,self.hw_spec)[0])
        #our current best
        cur_best=[{'ch_out_rf': 2, 'ch_out_noc': 8, 'ch_out_gb': 6, 'ch_out_dram': 1, 'ch_in_rf': 1, 'ch_in_noc': 1, 'ch_in_gb': 3, 'batch_rf': 1, 'batch_dram': 1, 'col_out_noc': 8, 'col_out_dram': 7, 'row_out_rf': 56, 'row_kernel_rf': 11, 'col_kernel_noc': 11},\
                  {'ch_out_rf': 1, 'ch_out_noc': 4, 'ch_out_gb': 16, 'ch_out_dram': 4, 'ch_in_rf': 8, 'ch_in_noc': 1, 'ch_in_gb': 12, 'batch_rf': 1, 'batch_dram': 1, 'col_out_noc': 27, 'col_out_dram': 1, 'row_out_rf': 27, 'row_kernel_rf': 5, 'col_kernel_noc': 5},\
                  {'ch_out_rf': 1, 'ch_out_noc': 6, 'ch_out_gb': 32, 'ch_out_dram': 2, 'ch_in_rf': 16, 'ch_in_noc': 2, 'ch_in_gb': 12, 'batch_rf': 1, 'batch_dram': 1, 'col_out_noc': 13, 'col_out_dram': 1, 'row_out_rf': 13, 'row_kernel_rf': 3, 'col_kernel_noc': 3},\
                  {'ch_out_rf': 1, 'ch_out_noc': 16, 'ch_out_gb': 16, 'ch_out_dram': 1, 'ch_in_rf': 16, 'ch_in_noc': 1, 'ch_in_gb': 24, 'batch_rf': 1, 'batch_dram': 1, 'col_out_noc': 13, 'col_out_dram': 1, 'row_out_rf': 13, 'row_kernel_rf': 3, 'col_kernel_noc': 3},\
                  {'ch_out_rf': 2, 'ch_out_noc': 4, 'ch_out_gb': 32, 'ch_out_dram': 1, 'ch_in_rf': 12, 'ch_in_noc': 2, 'ch_in_gb': 16, 'batch_rf': 1, 'batch_dram': 1, 'col_out_noc': 13, 'col_out_dram': 1, 'row_out_rf': 13, 'row_kernel_rf': 3, 'col_kernel_noc': 3}]
        print(arch_life(cur_best,self.stride_list,self.hw_spec)[0])
        #exit()
        
        
    def search(self,n=10000,mutate_init=False,init_multiplier=3):
        pop_list=[]
        #generate initial population
        if not mutate_init:
            for i in range(0,int(self.max_pop*init_multiplier)):
                pop_list.append(arch_random_pop(self.net_arch,self.df_order,self.arch_factor_list))
        else:
            pass
            
        #get the score for the initial population
        #print('evaluating the initial population')                             #maybe disregard unvalid over budege results  ? 
        score_board=[]                                                          #that will for sure increase the intial eval time a lot
        dump_yard=[]
        args1=list(range(0,len(pop_list)))
        output_q=Queue()
        def func1(i):
            #merged_child=merge_noc(pop_list[i],noc)
            merged_child=pop_list[i]
            try:
                output_q.put((i,arch_life(merged_child,self.stride_list,self.hw_spec,df_order=self.true_df_order)[0]),False)
            except Empty:
                raise Exception("There is no room in the queue in initial tiling factor evaluation stage")
        num_worker_threads=int(multiprocessing.cpu_count())
        multi_p(func1,args1,output_q,num_worker_threads,dump_yard)
        dump_yard=sorted(dump_yard)
        for idx in range(len(dump_yard)):
            score_board.append(dump_yard[idx][1])           
        #make sure nothing is wrong in the sorting process
        #print(arch_life(pop_list[0],self.stride_list,df_order=self.true_df_order)[0]==score_board[0])
        #initial ranking
        pop_list,score_board=pop_ranking(pop_list,score_board)
        #make sure nothing is wrong in the sorting process
        #print(arch_life(pop_list[0],self.stride_list,df_order=self.true_df_order)[0]==score_board[0])
        #print(score_board)
        #print('life cycles started')
        score1=0
        tmp_time=time.time()
        for _ in range(n):
            #if not saturate birth and mutate
            if len(pop_list) < self.max_pop:
                #para tasks
                num_worker_threads=int(multiprocessing.cpu_count())
                #print('generating pop')
                size=int(2*self.dying_rate*(self.max_pop))                                   # right now birth control is through max_pop; can be done through current pop
                if size%2 !=0:
                    size+=1
                #no task imbalance
                if num_worker_threads > (size/2):
                    num_worker_threads=int(size/2)
                if ((size/2)%num_worker_threads)!=0:
                    size=int(math.ceil((size/2.0)/num_worker_threads)*num_worker_threads*2)
                #print('new born size:',size)
                pos=list(range(0,size))
                shuffle(pos,random=random)
                #print(pos)
                #pos=np.random.randint(size,size=size)                                # only top "size" number of pop have rights of birth
                #new born
                tmp=time.time()
                score_pair=Queue()
                #pos needs to be changed
                def work(i):
                    new_child=arch_give_birth(pop_list[pos[i]],pop_list[pos[i+1]],self.net_arch)        #will try no birth only mutate next                          
                    new_child=arch_mutate(new_child,self.prop_m,self.arch_factor_list)            
                    #get the scores for the new born
                    #merged_child=merge_noc(new_child,noc)
                    merged_child=new_child
                    #print(arch_life(merged_child,self.stride_list)[0])
                    try:
                        score_pair.put((compress_dict(new_child),arch_life(merged_child,self.stride_list,self.hw_spec,df_order=self.true_df_order)[0]),False)
                    except Empty:
                        raise Exception("There is no room in the queue in tiling factor update stage")
                run_ites=int((len(pos)/2)//num_worker_threads)

                #how many runs we need 
                for run_ite in range(run_ites):
                    processes = [multiprocessing.Process(target=work, args=([i])) for i in range(2*run_ite*num_worker_threads,2*(run_ite+1)*num_worker_threads,2)]
                    #print(len(processes))
                    #print('queue size: ',score_pair.qsize())
                    for p in processes:
                        p.start()

                    while not score_pair.empty():
                        pair=score_pair.get()
                        pop_list.append(decompress_dict(copy.deepcopy(pair[0]),pop_list[-1]))
                        score_board.append(pair[1])

                    for p in processes:
                        p.join()
                    # alive_num=num_worker_threads
                    # while alive_num!=0:
                        # alive_num=0
                        # for p in processes:
                            # if p.is_alive():
                                # alive_num+=1
                        # print('alive p: ',alive_num)
                #clear score_pair in the queue to global
                while not score_pair.empty():
                    pair=score_pair.get()
                    pop_list.append(decompress_dict(copy.deepcopy(pair[0]),pop_list[-1]))
                    score_board.append(pair[1]) 
                #print('threading cost: ',time.time()-tmp)
            #else kill and birth and mutate
            else:
                #print(score_board)
                #print('killing')
                #rank
                #ganky way of sorting pop_list
                pop_list,score_board=pop_ranking(pop_list,score_board)
                #kill
                pop_list = pop_list[0:int((self.max_pop)*(1-self.dying_rate))]
                score_board=score_board[0:int((self.max_pop)*(1-self.dying_rate))]
                score1=score_board[0]
                self.best_score=score1
                self.best_dict=copy.deepcopy(pop_list[0])
                self.best_layer_breakdown=arch_life(pop_list[0],self.stride_list,self.hw_spec,df_order=self.true_df_order)[1]
                #print(self.best_layer_breakdown)
                #print('highest score: ',score1)
                #print(pop_list[0])
                #make sure nothing is wrong in the sorting process
                #print(arch_life(pop_list[0],self.stride_list,df_order=self.true_df_order)[0]==score_board[0])
                #print('energy_breakdown: ',simnas.sample_energy(pop_list[0][0],self.stride_list[0])[2])
                #print(time.time()-tmp_time)
                #tmp_time=time.time()       
                
        
#####################################
#parameters setup
#####################################    





###############################
#application level
###############################






                                                            

 
