/* Broadcast an Array
Rank 0 creates an array:
int arr[8] = {1,2,3,4,5,6,7,8};
Broadcast to all processes.
Each process computes local sum of entire array.*/

#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv)
{
    int rank, nprocs,arr[8],i,local_sum = 0,total_sum = 0;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    // array initialize by rank 0
    if(rank == 0)
    {
        int temp[8] = {1,2,3,4,5,6,7,8};
        for(i=0; i<8; i++)
            arr[i] = temp[i];
    }

    // array broadcast
    MPI_Bcast(arr, 8, MPI_INT, 0, MPI_COMM_WORLD);

    // sum of array
    for(i=0; i<8; i++)
    {
        local_sum += arr[i];
    }

    printf("Process %d Local Sum = %d\n", rank, local_sum);

    // adding all array sum by p0
    MPI_Reduce(&local_sum, &total_sum, 1,
               MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);

    if(rank == 0)
    {
        printf("Total Sum from all processes = %d\n", total_sum);
    }

    MPI_Finalize();
    return 0;
}
