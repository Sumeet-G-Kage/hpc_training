/*Master Collects Values
Each process computes:
value = rank * rank
Workers send value to rank 0 using MPI_Send.
Rank 0 receives all and prints total.*/



#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv)
{
    int rank,nprocs,value,total = 0;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    value = rank * rank;
    printf("Process %d value = %d\n", rank, value);
    if(rank != 0)
    {
        MPI_Send(&value, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);
    }
    else
    {
        for(int i=1; i<nprocs; i++)
        {
            MPI_Recv(&value, 1, MPI_INT, i, 0,
                     MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            total += value;
        }

        printf("Total using Send/Recv = %d\n", total);
    }

    MPI_Finalize();
    return 0;
}
