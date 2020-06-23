import math

# CONSTANTS
e = 0.25     # Todos los objetos dentro de un circulo de "radio" 45 grados los tomo como uno solo

def reduce_sources(sources):
    for o1 in sources:
        for o2 in sources:
            if o1 != o2:
                result = check_and_merge_objects(o1,o2)
                if len(result) == 1:
                    sources.remove(o1)
                    sources.remove(o2)
                    sources.append(result[0])
                    break
    
    if len(sources)>3:
        sources = keep_significant_sources(sources)
    #print(sources)
    return sources

def check_and_merge_objects(o1, o2):
    r1=math.sqrt(o1[0]**2 + o1[1]**2 + o1[2]**2)
    t1=math.atan2(o1[1],o1[0])
    f1=math.acos(o1[2]/r1)
    
    r2=math.sqrt(o2[0]**2 + o2[1]**2 + o2[2]**2)
    t2=math.atan2(o2[1],o2[0])
    if t2==-0:
        t2
    f2=math.acos(o2[2]/r2)
    
    if (abs(t2-t1)<e and abs(f2-f1)<e):
        #print("Object 1: {}".format([r1,t1,f1]))
        #print("Object 2: {}".format([r2,t2,f2]))
        r3 = min(r1,r2)
        t3 = (t1 + t2)/2
        f3 = (f1 + f2)/2
        o3 = [(r3*math.sin(f3)*math.cos(t3)),(r3*math.sin(f3)*math.sin(t3)),(r3*math.cos(f3))]
        #print("Object 3: {}".format([r3,t3,f3]))
        result = [o3]
    else:
        #print("Object 1: {}".format([r1,t1,f1]))
        #print("Object 2: {}".format([r2,t2,f2]))
        #print("Distance is {} and {}".format(abs(t2-t1),abs(f2-f1)))
        result = [o1, o2]
    return result

def keep_significant_sources(sources):
    sources = sorted(sources, key=lambda k: (math.sqrt(k[0]**2 + k[1]**2 + k[2]**2)))
    return sources[:3]

#sources=keep_significant_sources([[1,5,0],[0,1,0],[0,0,1],[1,1,1,]])
#print(sources)
