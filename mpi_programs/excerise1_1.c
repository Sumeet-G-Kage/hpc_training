#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

#define N 1000000   // change to 10000, 100000, 1000000

int main(int argc, char **argv)
{
    int rank, nprocs;
    int *arr;
    long long local_sum = 0, total_sum = 0;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    if(rank == 0)
    {
        printf("\nArray Size (N) = %d\n", N);
        printf("Number of Processes = %d\n\n", nprocs);
    }

    arr = (int*) malloc(N * sizeof(int));

    for(int i = 0; i < N; i++)
        arr[i] = 1;

    int count = N / nprocs;
    int start = rank * count;
    int stop  = start + count;

    MPI_Barrier(MPI_COMM_WORLD);   // synchronize before timing

    double start_time = MPI_Wtime();

    for(int i = start; i < stop; i++)
        local_sum += arr[i];

    double end_time = MPI_Wtime();

    double local_time = end_time - start_time;
    double total_time;

    // Combine total sum
    MPI_Reduce(&local_sum, &total_sum, 1,
               MPI_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);

    // Combine runtime (take maximum)
    MPI_Reduce(&local_time, &total_time, 1,
               MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    if(rank == 0)
    {
        printf("Total Sum = %lld\n", total_sum);
        printf("Total Runtime (Wall Time) = %f seconds\n\n", total_time);
    }

    free(arr);
    MPI_Finalize();
    return 0;
}
