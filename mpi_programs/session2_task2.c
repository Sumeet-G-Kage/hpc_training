/*Ring Communication
Each process sends its rank to the next process:
rank → (rank+1) % nprocs
Each process receives from previous rank and prints:
Rank X received Y */


#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv)
{
    int rank, nprocs,s_data, r_data,dest, source;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    s_data = rank;

    // use only this formula for next process
    dest = (rank + 1) % nprocs;

    // previous process without modulo
    if(rank == 0)
        source = nprocs - 1;
    else
        source = rank - 1;

    if(rank == 0)
    {
        MPI_Send(&s_data, 1, MPI_INT, dest, 0, MPI_COMM_WORLD);
        MPI_Recv(&r_data, 1, MPI_INT, source, 0,
                 MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    }
    else
    {
        MPI_Recv(&r_data, 1, MPI_INT, source, 0,
                 MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Send(&s_data, 1, MPI_INT, dest, 0, MPI_COMM_WORLD);
    }

    printf("Rank %d received %d\n", rank, r_data);

    MPI_Finalize();
    return 0;
}
