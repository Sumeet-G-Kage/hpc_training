#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int main(int argc, char **argv)
{
    int rank, nproc,N, *arr = NULL, *local_arr, loc_sum = 0, gl_sum = 0;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nproc);

    if(rank == 0)
    {
        printf("Enter N:\n");
	fflush(stdout);
        scanf("%d", &N);

        arr = (int*)malloc(N * sizeof(int));

        printf("Enter %d numbers:\n", N);
        for(int i=0; i<N; i++)
            scanf("%d", &arr[i]);
    }

    // Broadcast N
    MPI_Bcast(&N, 1, MPI_INT, 0, MPI_COMM_WORLD);

    // Allocate local array
    local_arr = (int*)malloc((N/nproc) * sizeof(int));

    // Scatter data
    MPI_Scatter(arr, N/nproc, MPI_INT,
                local_arr, N/nproc, MPI_INT,
                0, MPI_COMM_WORLD);

    // Local sum
    for(int i=0; i<N/nproc; i++)
        loc_sum += local_arr[i];

    printf("Process %d local sum = %d\n", rank, loc_sum);

    // Reduce to global sum
    MPI_Reduce(&loc_sum, &gl_sum, 1,
               MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);

    if(rank == 0)
    {
        float avg = (float)gl_sum / N;
        printf("Global Sum = %d\n", gl_sum);
        printf("Average = %f\n", avg);
    }

    free(local_arr);
    if(rank == 0)
        free(arr);

    MPI_Finalize();
    return 0;
}
