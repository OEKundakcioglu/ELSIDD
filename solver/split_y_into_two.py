import pickle

# from heuristic_profit import heuristic_with_U_cuts
from .trans_mip import heuristic_with_transportation


def PeriodDecomposition(instance, n_parts=2):
    
    '''
    -This function decomposes problem instance to 2 equal-sized-parts. Resulting subproblems have the same structure as the original problem.
    
    INPUT ARGS:
    -instance: Instance dictionary
    -n_parts: 2
    
    RETURN ARGS:
    -parts_list: a list containing subproblems.
    '''


    
    parts_list = []
    N, T, J = max(instance["u"].keys())
    part_size = T//n_parts
    mydct1 = {}
    mydct2 = {}
    
    for pkey in instance:
        mydct1[pkey] = {}
        mydct2[pkey] = {}
        for skey in instance[pkey]:
            if pkey in ["a","d","u"]:
                n,t,j = skey
                if t<=part_size:
                    mydct1[pkey][skey] = instance[pkey][skey]
                else:
                    mydct2[pkey][(n,t-part_size,j)] = instance[pkey][skey]
            
            if pkey in ["S","c","p"]:
                n,t = skey
                if t<=part_size:
                    mydct1[pkey][skey] = instance[pkey][skey]
                else:
                    mydct2[pkey][(n,t-part_size)] = instance[pkey][skey]

            if pkey == "h":
                n,t = skey
                if t<=part_size:
                    mydct1[pkey][skey] = instance[pkey][skey]
                if t>=part_size:
                    mydct2[pkey][(n,t-part_size)] = instance[pkey][skey]

            
            if pkey in ["B","C"]:
                t = skey
                if t<=part_size:
                    mydct1[pkey][skey] = instance[pkey][skey]
                if t>part_size:
                    mydct2[pkey][t-part_size] = instance[pkey][skey]

    parts_list.append(mydct1)
    parts_list.append(mydct2)
    
    return parts_list

"""
samples = pickle.load(open(f"samplesixtyfivefive.pkl", "rb"))

T, J, N, i =60,5,5,5
key = (T, J, N, i)
d = samples.get(key)

n_parts=2
split=PeriodDecomposition(d.get("dataset"),n_parts)
key1=(N,(T//n_parts),J)
key=(N,T,J)


res=(heuristic_with_transportation(split[0],key1,0,0))
k=list(res["I"].values())[-1]
t=list(res["I_prime"].values())[-1]

print((res["objective_value"]))  
"""
"""   
y_new=[]
total_time=0
for i in range(len(res)):  
    values=res[i]["y"].values()
    y_new=y_new+list(values)
    total_time=total_time+res[i]["time"]

k=list(d["dataset"]["c"].keys())
y_new=dict(zip(k,y_new))

 
for i in y_new.keys():
    if y_new[i]!=1 or y_new[i]!=0:
        y_new[i]=round(y_new[i])

initial_mip=heuristic_with_U_cuts(d.get("dataset"),d.get("dataset_DP"),y_new,key)
time_limit=1800
left_time=time_limit-total_time
print("starting_tabu")
tabu_result=tabu_function(key,d,y_new,left_time)
"""


"""
T,J,N,i = 60,7,5,1
key=(N,T,J)
dataset=pickle.load(open(f"dataset_{T}_{J}_{N}_{i}.pkl", "rb"))
datasetDP=pickle.load(open(f"datasetDP_{T}_{J}_{N}_{i}.pkl", "rb"))
d={}
d["dataset_DP"]=datasetDP
d["dataset"]=dataset
"""
"""
samples1 = pickle.load(open(f"samplefortyfivefive.pkl", "rb"))
results1=[]
for item in samples1.keys():
    T,J,N,i = item[0], item[1], item[2], item[3]
    key = (T,J,N,i)
    d = samples1.get(key)
    print(key)
    n_parts=2
    split=PeriodDecomposition(d.get("dataset"),n_parts)
    key1=(N,(T//n_parts),J)
    key=(N,T,J)
    res=[]
    res.append(heuristic_with_transportation(split[0],key1))
    I_prod=res[0]["I"][N,T//n_parts]
    els = list(res[0]["I_prime"].items())
    I_store=els[-1][1]
    res.append(heuristic_with_transportation_sec_part(split[1],key1,I_prod,I_store))
    results1.append(res)
    print((res[0]["objective_value"]))  
    print((res[1]["objective_value"])) 
"""   

   


   
  


    

    
