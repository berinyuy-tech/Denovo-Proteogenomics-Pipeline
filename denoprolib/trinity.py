import os, sys, re

def runTrinity(trinity_path, fastq, cpu, max_mem, output_dir):
    # Ensure non-empty directory
    if not os.listdir(fastq):
        sys.exit("Directory %s is empty." %fastq)
    else:
        contents = os.listdir(fastq)
        r1_pattern = re.compile('(.*)_R1.fastq$') # search for fastq files ending in '_R1'
        for i in range(len(contents)):
            if r1_pattern.match(contents[i]):
                id = contents[i].split('_R1')
                if id[0]+'_R2.fastq' in contents: # ensures only paired reads
                    print(id[0])
                    file1 = fastq + "/" + id[0] + "_R1.fastq"
                    print(file1)
                    file2 = fastq + "/" + id[0] + "_R2.fastq"
                    print(file2)
                    os.system(f"{trinity_path} --seqType fq --normalize_by_read_set"
                    + f" --left {file1} --right {file2} --trimmomatic --full_cleanup"
                    + f" --CPU {cpu} --max_memory {max_mem}G --bflyCPU 10 --bflyHeapSpaceMax 4G"
                    + f" --output {output_dir}/Trinity.{id[0]} --monitoring --verbose")

    