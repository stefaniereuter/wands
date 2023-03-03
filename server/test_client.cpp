#include <adios2.h>
#include <numeric>

template <class T>
void PrintData(std::vector<T> &data, size_t step)
{
    std::cout << " Step: " << step << " [";
    for (size_t i = 0; i < data.size(); ++i)
    {
        std::cout << data[i] << " ";
    }
    std::cout << "]" << std::endl;
}

int main()
{
    adios2::ADIOS adios;
    adios2::IO io = adios.DeclareIO("whatever");
    io.SetEngine("DataMan");
    io.SetParameters(
            {{"IPAddress", "127.0.0.1"}, {"Port", "8081"}, {"Timeout", "5"}});

    auto reader = io.Open("DataManReader", adios2::Mode::Read);

    adios2::Variable<float> floatArrayVar;
    std::vector<float> floatVector;

    while (true) {
        auto status = reader.BeginStep();
        if (status == adios2::StepStatus::OK) {
            floatArrayVar = io.InquireVariable<float>("/amc/AMC_PLASMA CURRENT/data");
            auto shape = floatArrayVar.Shape();
            size_t datasize = std::accumulate(shape.begin(), shape.end(), 1,
                                              std::multiplies<>());
            floatVector.resize(datasize);
            reader.Get<float>(floatArrayVar, floatVector.data(),
                              adios2::Mode::Sync);
            reader.EndStep();
            PrintData(floatVector, reader.CurrentStep());
        }
        else if (status == adios2::StepStatus::EndOfStream)
        {
            std::cout << "End of stream" << std::endl;
            break;
        }
    }

    reader.Close();

    return 0;
}