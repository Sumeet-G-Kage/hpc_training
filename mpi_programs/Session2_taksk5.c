/*Parallel Vector Addition
Task
Rank 0 creates two vectors:
A = {1,2,3,4,5,6,7,8}B = {8,7,6,5,4,3,2,1}
Steps:
Scatter A and B
Each process computes local sum
Gather results (or print locally)
C[i] = A[i] + B[i] */






#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv)
{
    int rank, nproc,N = 8;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nproc);

    int chunk = N / nproc;

    int A[8], B[8], C[8];
    int local_A[chunk], local_B[chunk], local_C[chunk];

    if(rank == 0)
    {
        int tempA[8] = {1,2,3,4,5,6,7,8};
        int tempB[8] = {8,7,6,5,4,3,2,1};

        for(int i=0;i<8;i++)
        {
            A[i] = tempA[i];
            B[i] = tempB[i];
        }
    }

    MPI_Scatter(A, chunk, MPI_INT,
                local_A, chunk, MPI_INT,
                0, MPI_COMM_WORLD);

    MPI_Scatter(B, chunk, MPI_INT,
                local_B, chunk, MPI_INT,
                0, MPI_COMM_WORLD);

    for(int i=0;i<chunk;i++)
    {
        local_C[i] = local_A[i] + local_B[i];
    }

    printf("Process %d computed: ", rank);
    for(int i=0;i<chunk;i++)
        printf("%d ", local_C[i]);
    printf("\n");

    MPI_Gather(local_C, chunk, MPI_INT,
               C, chunk, MPI_INT,
               0, MPI_COMM_WORLD);

    if(rank == 0)
    {
        printf("Final Vector C:\n");
        for(int i=0;i<chunk*nproc;i++)
            printf("%d ", C[i]);
        printf("\n");
    }

    MPI_Finalize();
    return 0;
}
