/*Master Collects Values
Each process computes:
value = rank * rank
Workers send value to rank 0 using MPI_Reduce
Rank 0 receives all and prints total */

#include<stdio.h>
#include<mpi.h>

int main(int argc, char **argv)
{
  int rank,nproc,value,total=0;
  MPI_Init(&argc, &argv);
  
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &nproc);
  
  value = rank*rank;
  printf("Process %d calculated %d\n",rank,value);
  MPI_Reduce(&value, &total, 1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);
 
  if(rank == 0)
  {
     printf("\nTotal using MPI_Reduce() = %d\n", total);
  }

  MPI_Finalize();
  return 0;
}
