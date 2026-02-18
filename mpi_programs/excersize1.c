#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 10000 // this changed accordingly

int main(int argc, char **argv)
{
    int rank, nprocs;
    int *arr;
    long long loc_sum = 0, t_sum = 0;
    clock_t start_clock, end_clock;

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

    MPI_Barrier(MPI_COMM_WORLD);

    start_clock = clock();

    for(int i = start; i < stop; i++)
        loc_sum += arr[i];

    end_clock = clock();

    double local_time =
        (double)(end_clock - start_clock) / CLOCKS_PER_SEC;

    printf("Process %d: CPU Time = %f sec, Local Sum = %lld\n",
           rank, local_time, loc_sum);

    double total_time;

    MPI_Reduce(&loc_sum, &t_sum, 1,
               MPI_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);

    MPI_Reduce(&local_time, &total_time, 1,
               MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    if(rank == 0)
    {
        printf("\nTotal Sum = %lld\n", t_sum);
        printf("Total Runtime (CPU) = %f seconds\n", total_time);
    }

    free(arr);
    MPI_Finalize();
    return 0;
}
