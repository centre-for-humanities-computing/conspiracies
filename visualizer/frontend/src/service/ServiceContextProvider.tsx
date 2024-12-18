import React, {
  createContext,
  PropsWithChildren,
  useContext,
  useState,
} from "react";
import { DocService } from "../docs/DocService";
import { GraphBackend } from "../../../backend/src/orms/core";
import { GraphService, HostedGraphService } from "./GraphService";

interface Services {
  getGraphService: () => GraphService;
  setGraphService: (service: GraphService) => void;
  getDocService: () => DocService;
  setDocService: (service: DocService) => void;
}

const ServiceContext = createContext<Services | undefined>(undefined);

export const ServiceContextProvider: React.FC<PropsWithChildren> = ({
  children,
}) => {
  const [graphService, setGraphService] = useState<GraphService | undefined>(
    undefined,
  );
  const [docService, setDocService] = useState<DocService | undefined>(
    undefined,
  );

  const value: Services = {
    getGraphService: () => {
      if (!graphService) {
        throw new Error("DocService has not been initialized!");
      }
      return graphService;
    },
    setGraphService: (service: GraphService) => setGraphService(service),
    getDocService: () => {
      if (!docService) {
        throw new Error("DocService has not been initialized!");
      }
      return docService;
    },
    setDocService: (service: DocService) => setDocService(service),
  };

  if (!graphService || !docService) {
    // const handleGraphFileLoaded = (data: any) => {
    //   setGraphService(new FileGraphService(data));
    // };
    //
    // const handleDocsFileLoaded = (data: any) => {
    //   setDocService(new FileDocService(data));
    // };

    // const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    //   const file = event.target.files?.[0];
    //   if (file) {
    //     setGraphService(new HostedGraphService(file.name))
    //   }
    // };

    return (
      <div className={"padded flex-container"}>
        {/*Load graph:&nbsp;*/}
        {/*<JsonFileUploadComponent onFileLoaded={handleGraphFileLoaded} />*/}
        {/*Load documents:&nbsp;*/}
        {/*<NdjsonFileUploadComponent onFileLoaded={handleDocsFileLoaded} />*/}
        Choose DB:&nbsp;
        <input type={"file"} />
        Mock:&nbsp;
        <button
          onClick={() =>
            fetch("http://localhost:5000/graph")
              .then((r) => r.json())
              .then((r) => console.log(r))
          }
        >
          Press
        </button>
      </div>
    );
  }

  return (
    <ServiceContext.Provider value={value}>{children}</ServiceContext.Provider>
  );
};

export const useServiceContext = (): Services => {
  const context = useContext(ServiceContext);
  if (!context) {
    throw new Error("useServiceContext must be used within a ServiceProvider");
  }
  return context;
};
