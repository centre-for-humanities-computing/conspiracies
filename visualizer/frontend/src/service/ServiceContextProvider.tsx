import React, {
  createContext,
  PropsWithChildren,
  useContext,
  useState,
} from "react";
import { DocService } from "../docs/DocService";
import { GraphService, GraphServiceImpl } from "./GraphService";

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
    new GraphServiceImpl("http://localhost:5000"),
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
